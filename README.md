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
   

* FullAccountReport.Py

    * Uses the graphql API report feature to download information on every device in the account

    * Note that this using the Account Key ID and  Key Secret, which is different from what is used on the other tools

    * Redirect the output to a file using > or pipe it into CSV Account Duplicates    

* RemoteIt-CSV-Duplicates.Py

    * Takes the output of the FullAccountReport.py and checks if there are any devices with Duplicate Names.
    * When there are duplicates it works out the most recent one and creates a script to delete the others, using RemoteIt-Delete.py

* RemoteIt-Delete.py
    * Deletes a devices from the account with the given Name that has the HW ID.
    * It will not delete a device that is only in the account once, unless you use the --Force option
    * Note that this API is not officially documented by Remote.It, but it is the same one the Web Page uses

* RemoteIt-Account-Summary.py
	*	Takes the FullAccountReport and computes a summary for the account, based on device model types.
	*  If a date is provided then only devices that have connected since then will be included in the summary

* DeviceList.py
	* 	Checks the account for errors, such as devices with an incorrect number of services.

	
* ScreenViewAccount.Py

    * Uses the graphql API to download information on every device in the account reports on if it has the ScreenView service.

    * Note that this using the Account Key ID and  Key Secret, which is different from what is used on the other tools
    
    * If the HTML ption is provided then a HTML format output will be created. If the device is active a link will be included allowing for the service to be connected to. This calls remote_screen_command

    * Redirect the output to a file using > 

* Remote_Screen

	CGI script that displays the account and allows connections

* remote_screen_connect

	CGI script that does the connection to a ScreenView session
	
*	Remote_Status

	CGI script that is the basis or the general display 	

   