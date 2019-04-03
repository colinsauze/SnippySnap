import os
import glob
import time
'''Generates a HTML report about each image we changed'''


def generate_report(report_filename):
    '''Generates an HTML report about which images have changed
    :param changed_image_list: The list of images which have changed
    :param unchanged_image_list: The list of images which haven't changed
    :param filename: The name of the report file
    '''

    unchanged_image_list = []
    changed_image_list = []

    for filename in glob.glob("outputs/screenshots/*.png"):
        basename = os.path.basename(filename)
        if os.path.exists("outputs/"+basename+".status") is True:
            statusfile = open("outputs/"+basename+".status", "r")
            status = statusfile.read()
            if status == "unchanged":
                unchanged_image_list.append(basename)
            elif status == "changed":
                changed_image_list.append(basename)

    print("unchanged files", unchanged_image_list)
    print("changed files", changed_image_list)

    report = open(report_filename, "w")

    report.write("<html>\n\t<head><title>Changed Images Report</title>")
    report.write("</head>\n\n")

    report.write("\t<body>\n")
    report.write("\t\t<h1>Changed Images Report</h1>\n")

    report.write("\t\t<p>Report Created at "+time.asctime()+"</p>\n")
    report.write("\t\t<h2>The following images have changed:</h2>\n")

    for image in changed_image_list:
        report.write("\t\t<p><a href=\"screenshots/" + image +
                     "\">screenshots/" + image + "</a>")

        report.write(" (<a href=\"report-"+image+"\">Old Image</a>)")
        report.write(" (<a href=\"comparison-"+image+"\">Changes Image</a>)")
        report.write(" (<a href=\"mask-"+image+"\">Mask Image</a>)\n")

    report.write("\t\t<h2>The following images are identical:</h2>\n")
    for image in unchanged_image_list:
        report.write("\t\t<p><a href=\"screenshots/" + image +
                     "\">screenshots/" + image + "</a>\n")

    report.write("\t</body>\n</html>")

    report.close()
