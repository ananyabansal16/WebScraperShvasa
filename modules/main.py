from init import load_env_vars
from scraper import init_webdriver, get_questions_from_google
from openai_client import init_openai, insert_answers_into_google_sheets, verify_and_update_answered_status
from sheets_client import init_google_sheets, insert_questions_into_google_sheets

def main(website, keyword, num_questions=10):
    if num_questions < 1 or num_questions > 50:
        print("The number of questions must be between 1 and 50. Please enter a value within this range.")
        return

    openai_api_key, credentials_json_path, gpt_model_name= load_env_vars()
    
    if isinstance(credentials_json_path, tuple):
        openai_api_key, credentials_json_path = credentials_json_path[0], credentials_json_path[1]

    openai_client = init_openai()
    sheets_client = init_google_sheets(credentials_json_path)

    questions = []
    total_extracted = 0
    driver = init_webdriver()

    while total_extracted < num_questions:
        batch_size = min(10, num_questions - total_extracted)  # Process in smaller batches to avoid timeouts
        batch_questions = get_questions_from_google(driver, website, keyword, batch_size)
        if not batch_questions:
            print("No more questions found on Google.")
            break

        questions.extend(batch_questions)
        total_extracted += len(batch_questions)
        insert_questions_into_google_sheets(sheets_client, batch_questions, keyword, website)
        print(f"Extracted {total_extracted} questions so far.")

        if total_extracted < num_questions:
            continue_prompt = input("Do you want to continue fetching more questions? (y/n): ").strip().lower()
            if continue_prompt != 'y':
                break

    driver.quit()
    print(f"Successfully extracted and saved {total_extracted} questions to Google Sheets.")
    
    verify_and_update_answered_status(sheets_client)
    insert_answers_into_google_sheets(sheets_client, openai_client, gpt_model_name)

if __name__ == "__main__":
    website = input("Enter the website name: ")
    keyword = input("Enter the keyword: ")
    num_questions = int(input("Enter the number of questions you want (1-50, default is 10): ") or 10)
    main(website, keyword, num_questions)

# able to scrap more than one search result page  ^^
# add an input counter and by default take it 10   ^^
# sentiment analysis ^^
# add google sheet and give link to the sheet instead ^^
# XPath of H3 tag  ^^
# extract date   ^^
# extract description   ^^
# fix credentials for github/ version control ^^
# selenium web driver
# question check edge cases ^^


# add model name to env ^^
# add an is_answered column 