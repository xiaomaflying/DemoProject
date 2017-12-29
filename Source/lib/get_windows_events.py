import win32evtlog
import win32con
import win32evtlogutil

import traceback
import time
import sys
import datetime
import locale

number_of_hours_to_look_back = 24


def date2sec(evt_date):
    dt = datetime.datetime.strptime(evt_date, "%a %b %d %H:%M:%S %Y")
    return dt.timestamp()


def readEventLog(server, log_type):
    '''
    Reads the log_type (e.g., "Application" or "System") Windows events from the
    specified server.
    '''
    begin_sec = time.time()
    begin_time = time.strftime('%H:%M:%S  ', time.localtime(begin_sec))

    seconds_per_hour = 60 * 60
    how_many_seconds_back_to_search = seconds_per_hour * number_of_hours_to_look_back

    gathered_events = []

    try:
        log_handle = win32evtlog.OpenEventLog(server, log_type)

        total = win32evtlog.GetNumberOfEventLogRecords(log_handle)
        print("Scanning through {} events on {} in {}".format(total, server, log_type))

        flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ

        event_count = 0
        events = 1
        while events:
            events = win32evtlog.ReadEventLog(log_handle, flags, 0)
            seconds = begin_sec
            for event in events:
                the_time = event.TimeGenerated.Format()
                seconds = date2sec(the_time)
                if seconds < begin_sec - how_many_seconds_back_to_search: break

                if event.EventType == win32con.EVENTLOG_ERROR_TYPE:
                    event_count += 1
                    gathered_events.append(event)
            if seconds < begin_sec - how_many_seconds_back_to_search: break  # get out of while loop as well

        win32evtlog.CloseEventLog(log_handle)
    except:
        try:
            print(traceback.print_exc(sys.exc_info()))
        except:
            print('Exception while printing traceback')

    return gathered_events


log_types = ["System", "Application", "Security"]
servers = ['127.0.0.1']

def main():
    all_events = dict()

    for server in servers:
        all_events[server] = dict()
        for log_type in log_types:
            all_events[server][log_type] = readEventLog(server, log_type)

    html_output_file = sys.argv[0].replace('.py', '.html')
    with open(html_output_file, "w") as out:
        locale.setlocale(locale.LC_ALL, 'english-us')

        out.write("""
            <style>
                body {{ Arial, "Helvetica Neue", Helvetica, sans-serif; }}
                table, th, td {{
                    border: 1px solid lightgray;
                }}
                table {{ border-spacing: 10px; }}
                th, td {{
                    border: none;
                }}
                th {{
                  background-color: darkgray;
                  color: yellow;
                }}
                td {{ vertical-align: text-top; }}
                .event-time {{ font-size: 9px; }}
                .event-type {{ font-size: 9px; }}
                .error-count {{ text-align: right; }}
    
            </style>
            We checked the {} logs on {} over the last {} hours.<br/>
        """.format(log_types, servers, number_of_hours_to_look_back))

        out.write("""
            <table>
            <tr>
                <th>Server</th>
                <th>Log</th>
                <th>Source</th>
                <th>Error count</th>
            </tr>
        """)
        for server in all_events:
            for log_type in all_events[server]:
                errors = dict()
                for event in all_events[server][log_type]:
                    if event.SourceName in errors:
                        errors[event.SourceName] += 1
                    else:
                        errors[event.SourceName] = 1

                for error in errors:
                    out.write("""
                        <tr>
                            <td>{}</td>
                            <td>{}</td>
                            <td>{}</td>
                            <td class="error-count">{}</td>
                        </tr>
                    """.format(server, log_type, error, locale.format("%d", errors[error], grouping=True)))

        out.write("""
            <table>
            <tr>
                <th>Server / Log</th>
                <th>Source/Date</th>
                <th>Text</th>
            </tr>
        """)

        for server in all_events:
            out.write('<tr><th colspan=3>{}</th></tr>'.format(server))
            for log_type in all_events[server]:
                for event in all_events[server][log_type]:
                    msg = str(win32evtlogutil.SafeFormatMessage(event, log_type))
                    msg = msg.replace('<', '&lt;')
                    msg = msg.replace('>', '&gt;')
                    if msg == "" or msg == None:
                        for s in event.StringInserts:
                            msg += "x {}<br/>".format(s)

                    out.write("""
                        <tr>
                            <td>{}<br/><span class="event-type">{}</span></td>
                            <td>{}<br/><span class="event-time">{}</span></td>
                            <td>{}</td>
                        </tr>\n""".format(event.ComputerName, log_type, event.SourceName, event.TimeWritten, msg))

        out.write("""
            </table>
        """)

    print("Wrote output to {}".format(html_output_file))

main()