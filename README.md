# Remote.it Tools

A Set of Tools for interacting with the Remote.IT api set.

* RemoteIt.Py

    * The module that does all of the interaction with the REST API

* Remote-Status.py
    * Provides information on devices that are in the account. By default only displays active units and services
    * Optionally displays all units, even if not active  --all
    * Optionally displays all Services, even if not active  --Services
    * Outputs a HTML version, requires jcmbsoft HTML_Unit

* RemoteIt-Check.py

    * A tool to check if a given device has the correct number of services registered.
    * Also supports reading a bulk pre-registration file , and checks all of the units in these files and creates files to delete the units and reload them.

* FullAccount.Py

    * Uses the graphql API to download information on every device in the account

    * Note that this using the Account Key ID and  Key Secret, which is different from what is used on the other tools

    * Redirect the output to a file using > or pipe it into Account Duplicates

* RemoteIt-Account-Duplicates.Py

    * Takes the output of the FullAccount.py and checks if there are any devices with Duplicate Names.
    * When there are duplicates it works out the most recent one and creates a script to delete the others, using RemoteIt-Delete.py

* RemoteIt-Delete.py
    * Deletes a devices from the account with the given Name that has the HW ID.
    * It will not delete a device that is only in the account once, unless you use the --Force option
    * Note that this API is not officially documented by Remote.It, but it is the same one the Web Page uses
