# carousel-updater
A no-code UI written in Python to update a simple JavaScript image carousel for a public school



The purpose of the project was to allow non-technical staff at the school to update the staff image carousel elements on the school website due to frequent staff changes.
I chose Python to write this in for the broad modules available and as a learning tool for myself.

The carousels are three individual HTML files using flickity JavaScript inline (live example here: https://belmont-h.schools.nsw.gov.au/about-our-school/our-staff.html)

The basics of the program are:

1. The script reads a ini file (in /config) to get the credentials and path needed for the SCP connection *This must be set prior to running the script*
2. os module and environment loader sets up the directory paths
3. A tkinter window is created with three workflows which correspond to the three HTML files to be generated (Head Teacher, Senior Executive, Year Advisor)
4. On submission of a collected entry (e.g. Name, Role, image, imagepath\**automatically collected*) the details a made into a class object and placed into the corresponding array. The form is then cleaned and the submitted entry appears in a list underneath the form. A dictionary is used to keep track of each submitted entry and it's corresponding delete button
5. The "Create & Send" button generates a HTML file using Jinja2 and the corresponding HTML template in /templates. A for loop iterates through the corresponding array and creates a cell in the carousel for each staff object. The HTML and image files are then sent to the webserver via SCP and replace the old carousel files. Before all this, on click the "Create & Send" button creates a window confirming the user action
6. The image assets are then cleaned from /html/staff-photos directory ready for the next workflow to run

