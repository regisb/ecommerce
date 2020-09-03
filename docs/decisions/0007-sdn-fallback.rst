6. Add fallback for ecommerce sdn check
------------------------------------------------------------

Status
------

Accepted (September 2020)

Context
-------

When learners attempt to place an order in ecommerce through our Cybersource flow, edX makes a call to the `ConsolidatedScreeningListAPI` at `trade.gov` to check that we are legally allowed to process the transaction for that learner.
The API has periods of downtime and although that downtime is often within the 99.5% uptime SLA of the service, edX would prefer to take extra precautions when downtime occurs to reduce our legal liability.
For this reason, we are developing a fallback that we can call when the API is down.
The design of the pre-existing calls to the API is out of scope for this ADR.

Decision
--------

`trade.gov` also provides a CSV alternative to the API, so we will leverage that option for the fallback by processing the CSV and storing the data which we'll be able to call as needed.

0. **Rejected Alternatives**
We considered switching over to making these export control checks in Cybersource.
We chose to continue making the existing calls to the SDN API and instead to implement a fallback mechanism to compensate for the downtime.
The reasons were that this would be less of a change relative to our current state and that the Cybersource checks would cost additional money.

1. **Using the CSV as a fallback vs as a primary solution**

We are only going to use the CSV when the API is down, not replace the API calls with the CSV. The reason is that the API is up the vast majority of the time and during that time we know the data is the most up to date, so the CSV makes more sense as a fallback rather than primary solution.

2. **Storing the data**

When activating the fallback one consideration was whether we would retrieve and process the CSV during the lifecycle of the request or do so ahead of time and store the data. The decision was to process the CSV in an automated job and store the data. 
One reason is that the fallback wouldn't work reliably if the CSV has periods of downtime like the API. With this approach we would use a request cache, but if the cache expired during downtime of the CSV then the fallback wouldn't have any data available. By storing the data there will always be a somewhat recent set of data to check the transaction against.
A second reason is that by having the processed data stored in a database, debugging of any production issues with the related code should be simpler.
This approach would have a more expensive engineering implementation cost, but we are willing to make that trade off.

3. **Denormalizing the data*

One option was to denormalize the data, where each row would be a unique combination of person, country, and type. The benefit would be having better performance in the query to filter the data, for example when filtering by country. However, more space would be used in the database since one record could have multiple rows.
The second option was to keep the data normalized, where we would have one row in the database per record in the CSV. This would more closely match the API and more closely match the data from the imported CSV. The database would also require less space.
We decided to go with keeping the data normalized because the performance gains of denormalizing would not be substantial enough to outweigh the costs to complexity and space.

4. **Allowing transactions**

If we are unable to check a transaction against the list we currently allow the transaction to succeed. The hope is that with the fallback in place, fewer transactions will fall through without being checked, and therefore allowing them will be less of a liability.

5. **Algorithm**

For the algorithm in the fallback to match name/address pairs to entries in the list we chose to attempt to replicate the algorithm used by the API as much as possible. Although we don't know what the exact algorithm is, we used some test queries to identify key properties of the algorithm and will implement the simplest algorithm that retains the same properties.

6. **Location of the code**

We decided to implement the fallback in ecommerce as opposed to its own repository because the primary SDN check is in ecommerce so it will live close to existing relevant code.

7. **Storing Import Metadata**
We had the option to store just the data from the CSV itself, or to also store metadata about the import. We chose to also store the metadata of when the list was downloaded/imported and which list is currently in use.
This may be helpful if we need to debug issues with the import or better understand the fallback behavior.

8. **Skipping over problematic rows during import**

We may not be able to process some rows during the import.
We considered failing the entire import due to a few problematic rows.
We considered skipping over those rows in favor of getting the most updated data.
We chose to skip over rows that we cannot process because having updated data outweighed missing a few records. We do compensate for this by ensuring the file meets a size threshold so that a near empty file woul not get imported.

9. **Retaining the properties of the API**

We would like the fallback to retain the properties of the API.
We could try to make the matching perform better, but instead we prioritized trying to make the matching behavior remain consistent with the matching done by the API.
By performing some test queries, a few properties of the API were identified:
1. Order of words within a name doesn’t matter
2. Number of times that a given word appears within a name appears doesn’t matter
3. Non-alpha characters between words or at the beginning/end of a given word don't matter
4. If a subset of words within a name match, it still counts as a match
5. Capitalization doesn’t matter
6. Primary names and alternate names are treated as one set of words
7. Some unicode characters like accented characters are transliterated
8. Similar properties are true for addresses
However, it is important to note that if the fallback was implemented to have these properties, this was only to match the API. If the properties of the API change, the behavior of the fallback would need to change as well.


Consequences
------------

When the `ConsolidatedScreeningListAPI` goes down, we will have a fallback option available to call.