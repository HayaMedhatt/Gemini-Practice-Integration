import google.generativeai as genai
import re  # For regex to remove markdown
from app.core.config import settings

# Configure the generative AI API
genai.configure(api_key=settings.GEMINI_API_KEY)

# Initialize the selected model
model = genai.GenerativeModel(model_name=settings.GEMINI_MODEL)  # Selected model

def remove_markdown(text):
    """
    Removes all markdown syntax from the given text, including headings (#) and other markdown symbols.

    Args:
        text (str): The text containing markdown.

    Returns:
        str: The cleaned text without markdown.
    """
    markdown_pattern = r'''
        (\*\*|__)             # Bold syntax (**text** or __text__)
        | (\*|_)              # Italic syntax (*text* or _text_)
        | (`|~|>)             # Inline code, strikethrough, or blockquote
        | (\[.*?\]\(.*?\))    # Links [text](url)
        | (!?\[.*?\]\(.*?\))  # Images and links with exclamation mark
        | (\n\s*[-*]\s)       # Unordered list
        | (\n\s*\d+\.\s)      # Ordered list
        | (\#.*)              # Headings (# Heading, ## Subheading, etc.)
    '''
    # Remove markdown syntax
    cleaned_text = re.sub(markdown_pattern, '', text, flags=re.VERBOSE)
    # Remove multiple spaces, tabs, or newlines
    return re.sub(r'\s+', ' ', cleaned_text).strip()

def paginate_text(text, max_length):
    """
    Splits the given text into chunks of the specified maximum length.

    Args:
        text (str): The text to paginate.
        max_length (int): The maximum length of each chunk.

    Returns:
        list: A list of text chunks.
    """
    if max_length <= 0:
        raise ValueError("max_length must be greater than 0.")

    # Split into words for smart pagination
    words = text.split()
    chunks, current_chunk = [], ""

    for word in words:
        if len(current_chunk) + len(word) + 1 > max_length:  # +1 for the space
            chunks.append(current_chunk.strip())
            current_chunk = word
        else:
            current_chunk += f" {word}"

    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

def gemini_response(text, input_token_limit=512, output_token_limit=512):
    """
    Generates a response from the generative AI model with pagination for both input and output.

    Args:
        text (str): The input text for the model.
        input_token_limit (int): The maximum allowed length for input text.
        output_token_limit (int): The maximum allowed length for output text.

    Returns:
        str: The model's paginated response.
    """
    if not text or not isinstance(text, str):
        raise ValueError("Input text must be a non-empty string.")

    # Remove markdown from input text
    cleaned_text = remove_markdown(text)

    # Paginate input to enforce token limits
    paginated_input = paginate_text(cleaned_text, input_token_limit)

    # Collect responses for each paginated input
    responses = []
    for chunk in paginated_input:
        try:
            response = model.generate_content(chunk)
            # Remove markdown from the output text
            cleaned_response = remove_markdown(response.text)
            # Paginate the cleaned output and add it to the responses
            paginated_output = paginate_text(cleaned_response, output_token_limit)
            responses.extend(paginated_output)
        except Exception as e:
            responses.append(f"Error generating response for chunk: {chunk[:50]}... - {str(e)}")

    return "\n--- Page Break ---\n".join(responses)
