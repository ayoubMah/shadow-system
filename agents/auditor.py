from agents.sovereign import nightly_audit
from agents.calendar_sync import fetch_todays_events

def run_audit():
    """Interactive function to collect user feedback and run the audit."""
    print("\n--- 🌑 SHADOW SYSTEM: NIGHTLY AUDIT 🌑 ---")
    
    # 1. Fetch Schedule
    print("Scanning daily schedule...")
    events = fetch_todays_events()
    
    logs = []
    
    # --- GITHUB PROXY CHECK ---
    from agents.github_proxy import check_github_activity
    has_code, git_summary = check_github_activity()
    if has_code:
        print(f"\n[PROXY] GitHub Activity Detected: {git_summary}")
        logs.append(f"GITHUB AUTO-VERIFICATION: {git_summary} (Verify +Intelligence)")
    # ---------------------------

    if not events:
        print("No specific events found in calendar.")
    
    # 2. Ask about each event
    for event in events:
        print(f"\nQuest Detected: {event}")
        while True:
            response = input("Did you clear this quest? (y/n/partial): ").strip().lower()
            if response in ['y', 'yes']:
                logs.append(f"COMPLETED: {event}")
                break
            elif response in ['n', 'no']:
                reason = input("Reason for failure? (Be honest): ")
                logs.append(f"FAILED: {event} - Reason: {reason}")
                break
            elif response in ['partial', 'p']:
                details = input("Explain the partial completion: ")
                logs.append(f"PARTIAL: {event} - Details: {details}")
                break
            else:
                print("Invalid input. Use y/n/partial.")
    
    # 3. Allow open-ended input
    print("\n--- Additional Report ---")
    extra = input("Any other training, learning, or notes? (e.g., 'Read 50 pages of Java docs'): ")
    if extra:
        logs.append(f"EXTRA ACTIVITY: {extra}")
        
    if not logs:
        print("No activity recorded. System entering sleep mode.")
        return

    # 4. Proof of Quest (Vision)
    image_path = None
    proof_check = input("\nDo you have visual proof (screenshot/photo) for any quest? (y/n): ").strip().lower()
    if proof_check in ['y', 'yes']:
        path = input("Enter absolute path to image: ").strip('"').strip("'")
        if os.path.exists(path):
            image_path = path
            logs.append(f"PROOF SUBMITTED: {path}")
        else:
            print("Image not found. Proceeding without proof.")

    # 5. Submit to Sovereign
    print("\n[SYSTEM] Analyzing performance patterns...")
    log_summary = "; ".join(logs)
    
    try:
        result = nightly_audit(log_summary, image_path) # Pass image_path
        print("\n--- 👑 SOVEREIGN VERDICT 👑 ---")
        print(result)
    except Exception as e:
        print(f"Error communicating with Sovereign: {e}")

if __name__ == "__main__":
    run_audit()
