import pypco
import datetime
import parsedatetime
import os
import re
from sys import platform
from will.mixins.naturaltime import NaturalTimeMixin
from plugins.pco import msg_attachment


# You need to put your Personal access token Application key and secret in your environment variables.
# Get a Personal Access Key: https://api.planningcenteronline.com/oauth/applications
# Application ID: WILL_PCO_APPLICATION_KEY environment variable
# Secret: WILL_PCO_API_SECRET environment variable

pco = pypco.PCO(os.environ["WILL_PCO_APPLICATION_KEY"], os.environ["WILL_PCO_API_SECRET"])

# Solution has been proposed. We will only return first plan from first campus and see if that works.


def get(set_date="sunday"):
    attachment_list = []
    print(set_date)
    # Get the Order of Service of a date and return a formatted string ready to send back.
    # This only works for future dates since PCO API doesn't let us quarry plans by date.
    cal = parsedatetime.Calendar()
    set_date, parse_status = cal.parse(set_date)
    set_date = datetime.datetime(*set_date[:6])
    # If you're running this on windows this needs to be: %#d rather than %-d
    set_date = set_date.strftime('%B %d, %Y')  # linux
    set_date = strip_leading_zeros(set_date)
    set_list = str(set_date)

    try:
        for site in pco.people.campuses.list():
            print("Working on:", site.name)
            for serviceType in pco.services.service_types.list():
                    for plan in serviceType.rel.plans.list(filter=['future']):
                        if set_date.lstrip('0') in plan.dates:
                            for items in plan.rel.items.list():
                                # set_list = "\n".join([set_list, site.name])
                                if items.attributes['item_type' ''] == 'header':
                                    set_list = "\n".join([set_list, "*" + str(items.title) + "*"])
                                elif items.attributes['item_type' ''] == 'song':
                                    set_list = "\n".join([set_list, "• _" + str(items.title) + "_"])
                                else:
                                    set_list = "\n".join([set_list, "• " + items.title])
                                if set_list == set_date:
                                    set_list = "Sorry, I couldn't fine a plan for that date ¯\_(ツ)_/¯"
                            if set_list is not set_date:
                                attachment_list.append(msg_attachment.
                                                       SlackAttachment(fallback=set_list,
                                                                       pco="services", text="\n".join([site.name,
                                                                                                       set_date,
                                                                                                       serviceType.name,
                                                                                                       set_list]),
                                                                       button_text="Open in Services",
                                                                       button_url="https://services.planningcenteronline."
                                                                                  "com/plans/" + plan.id))
                        set_list = ""
    except Exception as e:
        print(type(e))
        for serviceType in pco.services.service_types.list():
            for plan in serviceType.rel.plans.list(filter=['future']):
                if set_date.lstrip('0') in plan.dates:
                    for items in plan.rel.items.list():
                        # set_list = "\n".join([set_list, site.name])
                        if items.attributes['item_type' ''] == 'header':
                            set_list = "\n".join([set_list, "*" + str(items.title) + "*"])
                        elif items.attributes['item_type' ''] == 'song':
                            set_list = "\n".join([set_list, "• _" + str(items.title) + "_"])
                        else:
                            set_list = "\n".join([set_list, "• " + items.title])
                        if set_list == set_date:
                            set_list = "Sorry, I couldn't fine a plan for that date ¯\_(ツ)_/¯"
                    if set_list is not set_date:
                        attachment_list.append(msg_attachment.
                                               SlackAttachment(fallback=set_list,
                                                               pco="services", text="\n".join([serviceType.name,
                                                                                               set_date,
                                                                                               set_list]),
                                                               button_text="Open in Services",
                                                               button_url="https://services.planningcenteronline."
                                                                          "com/plans/" + plan.id))
    finally:
        return attachment_list


def strip_leading_zeros(date_str):
    date_str = date_str.replace(":0", "__&&")
    date_str = re.sub("0*(\d+)", "\g<1>", date_str)
    date_str = date_str.replace("__&&", ":0")
    return date_str


if __name__ == '__main__':
    date = "Aug 5"
    print("Getting set list for ", date)
    for x in get(date):
        print(x.slack())
