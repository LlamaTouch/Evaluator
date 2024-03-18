from typing import List

from ..task_trace import EssentialStateKeyword, UIState

app_to_package_name = {
    "ebay": "com.ebay.mobile",
    "booking": "com.expedia.bookings",
    "youtube_kid": "com.google.android.apps.youtube.kids",
    "calendar": "com.google.android.calendar",
    "facebook": "com.facebook.katana",
    "calculator": "com.google.android.calculator",
    "chrome": "com.android.chrome",
    "firefox": "org.mozilla.firefox",
    "instagram": "com.instagram.android",
    "excel": "com.microsoft.office.excel",
    "mcdonalds": "com.mcdonalds.app",
    "authenticator": "com.google.android.apps.authenticator2",
    "Microsoft Excel": "com.microsoft.office.excel",
    "Duolingo": "com.duolingo",
    "Microsoft Authenticator": "com.google.android.apps.authenticator2",
    "Booking.com": "com.expedia.bookings",
    "YouTube Kids": "com.google.android.apps.youtube.kids",
    "Calculator": "com.google.android.calculator",
    "Facebook": "com.facebook.katana",
    "Spotify": "com.spotify.music",
}


def check_install_match(gr_ui_state: UIState, exec_ui_state: UIState):
    # collect all installed apps in during task execution under the current UIState
    installed_apps: List[str] = []
    for line in open(exec_ui_state.installed_app_path):
        installed_apps.append(line.strip().lower())

    # extract all apps to check in the annotated UIState
    app_list = gr_ui_state.essential_state[EssentialStateKeyword.CHECK_INSTALL]
    for app in app_list:
        app_pkg_name = app_to_package_name[app]
        if app_pkg_name in installed_apps:
            continue
        else:
            return False

    print(
        f"[app installation] match success: '{gr_ui_state.vh_path}' with '{exec_ui_state.vh_path}'"
    )
    return True


def check_uninstall_match(gr_ui_state: UIState, exec_ui_state: UIState):
    # collect all installed apps in during task execution under the current UIState
    installed_apps: List[str] = []
    for line in open(exec_ui_state.installed_app_path):
        installed_apps.append(line.strip().lower())

    # extract all apps to check in the annotated UIState
    uninstall_app_list = gr_ui_state.essential_state[
        EssentialStateKeyword.CHECK_UNINSTALL
    ]
    for app in uninstall_app_list:
        app_pkg_name = app_to_package_name[app]
        if app_pkg_name in installed_apps:
            return False
        else:
            continue

    print(
        f"[app uninstallation] match success: '{gr_ui_state.vh_path}' with '{exec_ui_state.vh_path}'"
    )
    return True
