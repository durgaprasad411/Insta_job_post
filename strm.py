import streamlit as st
from main import create_job_posting_image
from PIL import Image
import os

st.set_page_config(
    page_title="Professional Job Post Generator",
    page_icon="📝",
    layout="centered"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .stTextInput input, .stTextArea textarea {
        padding: 12px !important;
        border-radius: 8px !important;
    }
    .stButton button {
        width: 100%;
        padding: 12px;
        border-radius: 8px;
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.title("📝 Professional Job Post Generator")
    st.markdown("Create Instagram-friendly job postings with dynamic sizing")

    with st.form("job_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            company = st.text_input("Company Name*", placeholder="Google")
            qualification = st.text_input("Qualification*", placeholder="B.Tech CS")
            experience = st.text_input("Years of Experience*", placeholder="3-5 years")
        
        with col2:
            salary = st.text_input("Salary/Package*", placeholder="₹10-12 LPA")
            location = st.text_input("Location*", placeholder="Bangalore")
            apply_link = st.text_input("Apply Link*", placeholder="https://company.com/careers")

        submitted = st.form_submit_button("Generate Job Post")
    
    if submitted:
        if not all([company, qualification, experience, salary, location, apply_link]):
            st.error("Please fill all required fields!")
            return

        job_data = {
            "Company Name": company,
            "Qualification": qualification,
            "Years of Experience": experience,
            "Salary": salary,
            "Location": location,
            "Apply Link": apply_link
        }

        with st.spinner("Creating professional job post..."):
            try:
                output_file = f"{company.replace(' ', '_')}_job_post.png"
                image_path = create_job_posting_image(job_data, output_file)
                
                st.success("Job post created successfully!")
                
                # Display the image
                image = Image.open(image_path)
                st.image(image, caption="Your Job Post", use_column_width=True)
                
                # Download button
                with open(image_path, "rb") as file:
                    btn = st.download_button(
                        label="Download Image",
                        data=file,
                        file_name=output_file,
                        mime="image/png"
                    )
                
                # Clean up
                os.remove(image_path)
                
            except Exception as e:
                st.error(f"Error generating image: {str(e)}")

if __name__ == "__main__":
    main()