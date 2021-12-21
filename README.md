#Remote.it Tools

A Set of Tools for interacting with the Remote.IT api set.

* RemoteIt.Py

The module that does all of the interaction with the REST API

* Remote-Status.py
	* Provides information on devices that are in the account. By default only displays active units and services
	* Optionally displays all units, even if not active  --all
	* Optionally displays all Services, even if not active  --Services
	* Outputs a HTML version, requires jcmbsoft HTML_Unit

* RemoteIt-Check.py

	* A tool to check if a given device has the correct number of services registered. 
	* Also supports reading a bulk pre-registration file , and checks all of the units in these files and creates files to delete the units and reload them.
