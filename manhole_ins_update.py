"""Python toolbox that allows staff to update the Manhole inspections
Feature class () from the Accela Manhole Inspections
View (). Updates inspection condition class rows from ARCGIS ENTERPRISE REST API, based on date. 

Created by Heath Johnson on March 2023
"""



import os
import arcpy
from arcgis.gis import GIS
import datetime
from arcgis.features import FeatureLayer
from socket import gethostname
from tempfile import TemporaryDirectory


def main():
    try:
        # connect to oracle database     
        manholes = r""
        
        # connect to EnterpriseGIS database
        logging("Connecting to EnterpriseGIS database")
        gis = GIS("")
        

        # import data from EnterpriseGIS via the feature layer
        mi_dict_when = "INSPECTION_DATE >= CURRENT_DATE()-1"
        manhole_inspection = FeatureLayer(r"")
        manhole_inspection_fset = manhole_inspection.query(where=mi_dict_when)
        mh_fields = ['eid', 'condition', 'inspection_date']

        # Dictionary that removes the eid's from the inspection attributes
        mi_dict = {}
        for feature in manhole_inspection_fset.features:
            attributes = feature.attributes
            eid = attributes.pop('eid')
            mi_dict[eid] = attributes
        for k,v in mi_dict.items():
            logging(k, v)

        # Update attributes based on date and condition.
        # CRUD -> Target Dataset
        logging(("Searching Database for updates"))
        with arcpy.da.UpdateCursor(manholes, mh_fields) as mh_cursor:
            for mh in mh_cursor:
                if mh[0] in mi_dict.keys():
                    mh_key = mh[0]
                    # if the manhole inspection has not changed ignore it
                    if mh[1] != mi_dict[mh_key]['condition'] or mh[2] != mi_dict[mh_key]['inspection_date']:
                        # if either the date or the condition has been changed, update using the updaterow cursor.
                        mh[1] = mi_dict[mh_key]['condition']
                        # ARCGIS datetime needs to be a specific format. Dividing time by 1000 to remove the milliseconds.
                        mh[2] = datetime.datetime.fromtimestamp(mi_dict[mh_key]['inspection_date']/1000)
        logging("Success")

    except Exception as err:
        print(err)


# Script start
if __name__ == '__main__':
    # Define database logging properties.
    taskID = 
    task_status = "SUCCESS"
    task_msg = ""


    # Initialize file logging.
    logging = coc.initLogging()
    logging.coc_info(f"{os.path.basename(__file__)} (TaskID {taskID}) started on {gethostname()}")

    # Create basic email subject line with name of script
    email_subject = os.path.basename(__file__)

    # Set environments and update email subject line.
    gis_env = coc.Env("")
    logging(f"{gis_env.instance} instance set.")
    email_subject = f"{email_subject} [{gis_env.instance.upper()}]"
    accela_env = coc.Env("")
    logging(f"{accela_env.instance} instance set.")
    email_subject = f"{email_subject} [{accela_env.instance.upper()}]"

    try:
        # Prevent logging geoprocessing metadata and history.
        # In a script, metadata and history logging are activated by default.
        arcpy.SetLogMetadata(False)
        arcpy.SetLogHistory(False)

        # Run core functions
        with TemporaryDirectory() as temp_dir:
            main()

    except Exception as e:
        print(e)
        logging("An Exception Occurred.")
        task_status = "FAIL"
        task_msg = e
    finally:
        # Log script result in database
        try:
            logging(f"Log {task_status} result in database.")
            gis_env.updateScheduledTaskLog(taskID, task_status, task_msg)
        except Exception as e:
            print(e)
            logging("Error logging to database.")
            pass
        # Cleanup
        try:
            arcpy.management.ClearWorkspaceCache()
        except Exception as e:
            print(e)
            logging("Error trying gis_env.updateScheduledTaskLog()")
            pass
        # Send log file as email
        try:
            logging.coc_info("Send log file as email.")
            log_file_path = logging.root.handlers[0].baseFilename
            with open(log_file_path) as log_file:
                log_file_content = log_file.read()
                # Update email subject line with noteworthy log levels.
                for log_level in ["WARNING", "ERROR", "CRITICAL"]:
                    line_to_find = f" {log_level} "
                    if line_to_find in log_file_content:
                        email_subject = f"[{log_level}] {email_subject}"
                # Send the email.
                recipients = coc.sendEmail(
                    subject=email_subject,
                    body_content=log_file_content,
                    to=[""]
                )
                logging(f"Email sent to {recipients}")
        except Exception as e:
            print(e)
            logging("Error trying coc.sendEmail()")
            pass