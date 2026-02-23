"""
Subscription window - shown when required_action exists
"""
import customtkinter as ctk
import webbrowser


def show_subscription_window(user_data: dict):
    """Show subscription required window"""
    root = ctk.CTk()
    root.title("Subscription Required")
    root.geometry("600x450")
    root.resizable(False, False)
    root.eval('tk::PlaceWindow . center')
    
    title = ctk.CTkLabel(
        root,
        text="🔒 Subscription Required",
        font=("Arial", 20, "bold")
    )
    title.pack(pady=40)
    
    info = ctk.CTkLabel(
        root,
        text=f"Email: {user_data['email']}\nCurrent Tier: {user_data['tier']}",
        font=("Arial", 12)
    )
    info.pack(pady=15)
    
    message_text = user_data.get('required_action', {}).get(
        'message',
        'Please subscribe to continue using the application.'
    )
    message = ctk.CTkLabel(
        root,
        text=message_text,
        font=("Arial", 13),
        wraplength=500
    )
    message.pack(pady=30)
    
    btn_frame = ctk.CTkFrame(root, fg_color="transparent")
    btn_frame.pack(pady=40)
    
    def open_subscription():
        action_url = user_data.get('required_action', {}).get('action_url')
        if action_url:
            webbrowser.open(action_url)
    
    subscribe_btn = ctk.CTkButton(
        btn_frame,
        text="Open Subscription Page",
        command=open_subscription,
        width=220,
        height=45,
        font=("Arial", 13, "bold"),
        fg_color="#1f538d",
        hover_color="#14375e"
    )
    subscribe_btn.pack(side="left", padx=10)
    
    exit_btn = ctk.CTkButton(
        btn_frame,
        text="Exit",
        command=root.destroy,
        width=120,
        height=45,
        font=("Arial", 13)
    )
    exit_btn.pack(side="left", padx=10)
    
    root.mainloop()


def show_no_access():
    """Show generic no access window"""
    root = ctk.CTk()
    root.title("Access Denied")
    root.geometry("500x250")
    root.resizable(False, False)
    root.eval('tk::PlaceWindow . center')
    
    label = ctk.CTkLabel(
        root,
        text="🔒 Access Denied\n\nYou don't have access to this application.",
        font=("Arial", 14),
        wraplength=450
    )
    label.pack(pady=60)
    
    btn = ctk.CTkButton(
        root,
        text="Exit",
        command=root.destroy,
        width=120,
        height=35
    )
    btn.pack(pady=20)
    
    root.mainloop()
