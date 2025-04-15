from google import genai
import requests
from bs4 import BeautifulSoup
from readability import Document
from dotenv import load_dotenv
import os
load_dotenv()

client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
def is_link_working(url):
    try:
        response = requests.get(url, timeout=7)
        return response.status_code == 200, response
    except Exception as e:
        print(f"Error accessing {url}: {e}")
        return False, None

def extract_summary_from_html(html):
    try:
        doc = Document(html)
        summary_html = doc.summary()
        soup = BeautifulSoup(summary_html, 'html.parser')
        text = soup.get_text(separator='\n').strip()
        
        # Limit summary to 1000 characters
        return text[:1000]
    except Exception as e:
        print(f"Error summarizing HTML: {e}")
        return "Could not extract meaningful summary."

possible_labels = [
    "correct",
    "partially correct",
    "outdated",
    "wrong",
    "irrelevant",
    "no_answer",
    "hallucinated",
    "link_not_working",
    "incomplete"
]

def build_prompt(question, model_name, response_text, link=None, link_data=None, link_working=True):
    base_prompt = f"""You are evaluating a response from a language model.

    Question: {question}

    Model: {model_name}

    Model's response: {response_text}
    """
    if link:
        if link_working:
            base_prompt += f"""
    The model also provided this link: {link}
    The content from the link is summarized as: {link_data}
    """
    else:
        base_prompt += f"""
        The model also provided this link: {link}, but the link is not working.
        """

    base_prompt += f"""
    Label this response as one of the following: {', '.join(possible_labels)}.

    Provide:
    - Label: (one of the above)
    - One-line reason for the label.
    """

    return base_prompt

question = 'What was the name of the 1960s U.S. political movement against racial segregation?'
model_name = 'Grok + DeepSearch'
response_text = f"""# The Civil Rights Movement: America's Struggle Against Racial Segregation in the 1960s 
 
 The **Civil Rights Movement** was the defining U.S. political and social movement of the 1960s aimed at dismantling racial segregation and securing legal equality for African Americans. Emerging from decades of systemic discrimination under Jim Crow laws, this grassroots campaign employed nonviolent protests, legal challenges, and civil disobedience to challenge segregation in schools, public spaces, and voting booths. Its achievements—including landmark legislation like the **Civil Rights Act of 1964** and the **Voting Rights Act of 1965**—transformed American society and inspired global human rights struggles. 
 
 ---
 
 ## Origins and Key Objectives 
 
 ### Roots in Post-War Activism 
 The movement built on earlier efforts, such as the 1954 *Brown v. Board of Education* Supreme Court ruling that declared school segregation unconstitutional[7]. However, progress remained slow, particularly in the South, where "Massive Resistance" campaigns defied integration[1]. By the 1960s, activists shifted toward direct action to accelerate change. 
 
 ### Core Goals 
 - **Desegregation**: Ending "separate but equal" policies in schools, transportation, and public facilities[5]. 
 - **Voting Rights**: Overcoming barriers like literacy tests and poll taxes that disenfranchised Black voters[3]. 
 - **Economic Justice**: Addressing employment discrimination and poverty in African American communities[6]. 
 
 ---
 
 ## Major Campaigns and Protests 
 
 ### Sit-Ins and Student Activism 
 The movement gained momentum on **February 1, 1960**, when four Black students staged a sit-in at a segregated Woolworth’s lunch counter in Greensboro, North Carolina[3][6]. This tactic spread rapidly, with over 50,000 participants joining similar protests across the South by year’s end[6]. The **Student Nonviolent Coordinating Committee (SNCC)**, formed in April 1960, became a driving force in organizing youth-led demonstrations[2]. 
 
 ### Freedom Rides (1961) 
 To challenge segregation in interstate travel, activists organized **Freedom Rides**, testing compliance with the 1960 *Boynton v. Virginia* ruling. Mobs attacked riders in Alabama, firebombing buses and beating protesters, but the campaign pressured the Interstate Commerce Commission to enforce desegregation[2][6]. 
 
 ### Birmingham Campaign (1963) 
 The **Southern Christian Leadership Conference (SCLC)**, led by Dr. Martin Luther King Jr., targeted Birmingham, Alabama—a bastion of segregation. Police chief Bull Connor’s use of dogs and fire hoses against peaceful marchers, including children, drew national outrage and spurred federal intervention[2][8]. 
 
 ### March on Washington (1963) 
 A watershed moment occurred on **August 28, 1963**, when 250,000 people gathered in Washington, D.C. Dr. King’s "I Have a Dream" speech crystallized the movement’s vision, amplifying demands for congressional action[3][7]. 
 
 ### Selma to Montgomery Marches (1965) 
 The violent suppression of voting rights marchers on **Bloody Sunday** (March 7, 1965) at Selma’s Edmund Pettus Bridge galvanized support for the Voting Rights Act. Televised images of state troopers attacking protesters forced President Lyndon B. Johnson to prioritize legislative reform[3][8]. 
 
 ---
 
 ## Legislative Victories 
 
 ### Civil Rights Act of 1964 
 This landmark law: 
 - Banned segregation in public accommodations (restaurants, theaters) and employment discrimination[4][8]. 
 - Empowered federal enforcement through the Justice Department[1]. 
 
 ### Voting Rights Act of 1965 
 - Outlawed discriminatory voting practices, leading to a surge in Black voter registration in the South[3][8]. 
 - Authorized federal oversight of election administration in states with histories of disenfranchisement[7]. 
 
 ---
 
 ## Key Figures and Organizations 
 - **Martin Luther King Jr.**: The movement’s most prominent leader, advocating nonviolent resistance[7][8]. 
 - **SNCC and CORE**: Student and grassroots groups that organized sit-ins and freedom rides[2][6]. 
 - **Malcolm X**: A vocal advocate for Black empowerment, offering a contrast to King’s integrationist approach[8]. 
 
 ---
 
 ## Legacy and Ongoing Challenges 
 While the movement dismantled legal segregation, it faced criticism for insufficiently addressing economic inequality. Modern movements like Black Lives Matter continue its work, confronting systemic racism and police brutality. The Civil Rights Movement’s strategies—nonviolent protest, coalition-building, and legal advocacy—remain blueprints for social justice efforts worldwide[7][8]. 
 
 In conclusion, the **Civil Rights Movement** of the 1960s stands as a transformative chapter in U.S. history, dismantling Jim Crow segregation and redefining the nation’s commitment to equality. Its legacy endures in ongoing struggles for racial justice and democratic inclusion.
"""
# link = 'https://www.nps.gov/subjects/civilrights/modern-civil-rights-movement.htm'
link = None
link_working, response = is_link_working(link)
if link_working:
    link_data = extract_summary_from_html(response.text)
else:
    link_data = None
    link_working = False
prompt = build_prompt(question, model_name, response_text, link, link_data, link_working)
print(prompt)
# response = client.models.generate_content(
#     model="gemini-2.0-flash", contents=prompt
# )
# print(response.text)