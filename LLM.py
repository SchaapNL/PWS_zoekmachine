import ollama
import json

def call_tev1(authors, context):
    options = {str(author.get("id")): json.dumps(author, ensure_ascii=False) for author in authors}
    context["text"] = context["text"][:800]

    try:
        response = ollama.systemone(
            model='tev1:4b',
            state= f"Which Author fits the best for the text: [{context.get("title")}]" +
                    f"Which was writen in: [{context.get('date')}]" +
                    f"This is a snippet of the text: [{context.get('text')}]",
            questions={
                'best': {
                    'type': 'choice',
                    'instructions': 'What author wrote this? If it is unlikely that one of them wrote this return none.',
                    'criteria': options,
                },
            },
        )
    except ollama.ResponseError as e:
        if e.status_code == 400 and "context size" in str(e):
            print("Prompt too large, try fewer or shorter candidates.")
        else:
            print(f"Ollama error {e.status_code}: {e.error}")
        return None

    response = response.answers['best']
    if response is None:
        return None

    # response.get returns a string, so it needs to be parsed to compare it.
    id = int(response.get("choice"))
    return next((author for author in authors if author.get("id") == id), None)


def get_correct_author(authors, context):
    while len(authors) > 1 or authors is None:
        filtered = []

        #  By grouping it, it's easier to stay in the AI's context window and it will give more accurate results
        for group in chunker(authors, 5):
            best = call_tev1(group, context)

            if best is not None:
                filtered.append(best)

        authors = filtered

    if authors is None or len(authors) == 0:
        print("No authors found")
        return None

    return authors[0]

def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))