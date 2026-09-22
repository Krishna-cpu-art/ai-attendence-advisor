import streamlit as st
from google import genai

# Initialize the client. Replace 'YOUR_API_KEY' with your actual key.
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

def check_attendance(present, total):
    # Returns both the string and the percentage for routing
    if total == 0:
        return "No classes held yet.", None
    if present > total:
        return "Error: Present classes cannot be greater than total classes.", None

    current_percent = (present / total) * 100

    if current_percent >= 75.0:
        max_total = int(present / 0.75)
        can_miss = max_total - total
        return f"Attendance: {current_percent:.1f}%. Safe to miss: {can_miss}.", current_percent
    else:
        needed = (3 * total) - (4 * present)
        return f"Attendance: {current_percent:.1f}%. Need to attend: {needed} consecutive classes.", current_percent

def get_ai_advice(raw_stats):
    # Instruct Gemini on its persona and give it the data
    prompt = f"""
    You are a witty, slightly sarcastic but helpful senior student at an engineering college. 
    A junior just showed you these attendance stats: {raw_stats}
    
    If they are safe (>= 75%), tell them they can chill and mention how many classes they can bunk.
    If they are in the danger zone (< 75%), give them a reality check and clearly state exactly how many consecutive classes they need to attend to become eligible for exams.
    Keep it strictly under 3 sentences. Use a conversational, peer-to-peer tone.
    """
    
    # Call the model
    response = client.models.generate_content(
        model='gemini-3.5-flash',
        contents=prompt
    )
    return response.text

def main():
    st.title("🎓 AI Attendance-Eligibility Advisor")
    st.write("Enter your current attendance details below.")
    
    present = st.number_input("Classes Present", min_value=0, step=1)
    total = st.number_input("Total Classes Held", min_value=0, step=1)
    
    if st.button("Check Eligibility"):
        raw_stats, percent = check_attendance(present, total)
        
        # Display an error if input is invalid (e.g., total=0)
        if percent is None:
             st.error(raw_stats)
        else:
             st.info(f"📊 Raw Math: {raw_stats}")
             
             # Show a loading spinner while waiting for the API
             with st.spinner("Generating AI advice..."):
                 ai_message = get_ai_advice(raw_stats)
                 st.success(ai_message)

if __name__ == "__main__":
    main()