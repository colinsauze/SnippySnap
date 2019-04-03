
### Problem

User Documentation for applications with GUIs is time consuming to write. Much of the time is spent preparing screenshots to embed in the documentation. This requires setting up the GUI in the particular way required, with the appropriate data so that features such as the items in a drop down menu are visible in the shot. It may also involve cropping the image and highlighting a particular area to indicate to the user which button to press or which region of the screen is being discussed in the documentation. If anything changes in the GUI design, text or layout during the further development of the application then all screenshots need to be taken again to keep documentation up to date and avoid confusing the users.

If this process of capturing the screenshots could be automated it would not only speed up the process but might also encourage user documentation to be written earlier in the development process since there would be less concern about later GUI changes requiring huge amounts of repeated work.

### Proposed Solution

Due to the expertise of the group our solution focuses on browser based GUIs and builds on the Selenium web browser automation framework using Python 3. Selenium already has a screenshot function and we will provide an alternative to this which can be called to provide additional functionality.

The function will be:

* Take a screenshot using the standard Selenium screenshot function
* Save the screenshot with the filename specified by the user
* Compare the screenshot image to the same screenshot image from the previous run (if there is one)
* Flag any differences to the user for checking


#### Screenshot workflow

The user automates the browser interactions to the point where the screenshot should be taken for the documentation. This can either be done in a test environment where the data can be controlled or in the 'real world'. The SnippySnap screenshot function is called to take the screenshot. Automation can continue and further screenshots can be taken in the same browser instance.

It will be up to the user to decide the best way to structure the automation of their application. Because it can take some time to reach the appropriate point in a GUI for a screenshot to be captured it is best to automate each section of documentation as a single browser instance in Selenium so that actions do not have to be repeated. Alternatively each screenshot could be controlled by an individual script using a separate browser instance.

When the screenshots have all been generated the user should check the report produced to confirm if any of the screensht have changed since the last run. The user can then act on this infomation by updating the documentation to reflect the new screenshot or solving any problems with the screenshot.


#### Proposed Integration Workflow

The ideal way to integrate this into a project is to include it in a continuous integration workflow. This would run tests, retake screenshots and rebuild the documentation using the new screenshots.

#### Future Developments

This proof of concept tool would benefit from many additions.

We would like to add:


* The ability to integratge this into a variety of workflows which could ionclude comtinious integration tests with systems such as Jenkins, the development of tutorials and training materials.
* The ability to capture a screen shot of a specified area of a screen rather than always the whole screen or to be able to automatically crop the image perhaps using imageMagick or a similar command line package.
* The ability to annotate a screenshot to highlight a particular area such as a button or text field.
* Improving the SnippySnap tool to work with non-browser based GUIs such as ImageJ and ParaView (this would need an alternative automation tool as Selenium only works with browsers).



### Initial Development Road Map

This file provides information of features that we would like to include in this tool:
1, Simplest use case - automate a screen shot of a GUI web app into html documentation. 
2, Next use case is to campare this image with the previous image. If the previous image is different repace the screen shot in the html documentation. 
3, Create a list of screen shots of a GUI web app for a functional section. 
4, Trgger the running of the tool by a python script per image with a master python script to run it all.

