SnippySnap Project Outline
--

### Problem

User Documentation for applications with GUIs is time consuming to write. Much of the time is spent preparing screenshots to embed in the documentation. This requires setting up the GUI in the particular way required, with the appropriate data and so that the any features such as the items in a drop down menu are visible in the shot. It may also involve highlighting a particular area of the image to indicate to the user what button to press or what region of the screen is being discussed in the documentation. If anything changes in the GUI design, text or layout during the further development of the project then all screenshots need to be taken again to keep documentation up to date and avoid confusing users.

If this process of taking the screenshots could be automated in the same way as tests it would not only speed up the process but might also encourage user documentation to be written earlier in the development process since there would be less concern about later GUI changes requiring huge amounts of repeated work.

### Proposed Solution

Due to the expertise of the group our solution will focus on browser based GUIs and build on the Selenium automation framework using Python. Selenium already has a screenshot function and we will provide an alternative to this which can be called to provide additional functionality.

The function will:

* Take a screenshot using the standard Selenium screenshot function
* Save the screenshot with the filename specified by the user
* Compare the screenshot image to the same screenshot image from the previous run (if there is one)
* Flag any differences to the user for checking
* Optionally annotate an area of the screenshot for use in the documentation

#### Screenshot workflow

The user automates the browser interaction to the point that the screenshot should be taken for the documentation. This can either be done in a test environment where the data can be controlled or in the 'real world'. The SnippySnap screenshot function is called to take the screenshot. Automation can continue and further screenshots can be taken in the same browser instance.

It will be up to the end user to decide the best way to structure the automation for their application. Because it can take some time to reach the appropriate point in a GUI for a screenshot it might be best to automate each section of documentation as a single browser instance in Selenium so that actions do not have to be repeated. Alternatively each screenshot could be controlled by an individual script using a separate browser instance.

When the screenshot have all been generated the user should check the report produced to confirm if any of the screensht have changed since the last run. The user can then act on this infomation by updating the documentation to reflect the new screenshot or solving any problems with the screenshot.


#### Proposed Integration Workflow

The ideal way to integrate this into a project is to include it in a continuous integration workflow. This would run tests, retake screenshots and rebuild the documentation using the new screenshots.
