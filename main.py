from flask import Flask, request, jsonify, render_template
import key
import openai
import prompts
openai.api_key = key.KEY

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('./chathtml.html')


# The above function returns the HTML code to be displayed on the page


@app.route('/process_qtc', methods=['POST', 'GET'])
def process_message():
    results = None
    if request.method == "POST":
        message_data = request.get_json()
        #        print(message_data)
        reply = get_reply(message_data)
        results = {'processed': 'true', 'reply': reply}
    return jsonify(results)

premise = prompts.prefix + " " + prompts.premise_11


send = [
    {"role": "system", "content": premise},
]

send.append({"role": "assistant", "content": prompts.premise_11_support_1})
send.append({"role": "user", "content": prompts.premise_11_support_2})

def openai_fetch_mesage(send):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=send,
    )
    return response['choices'][0]['message']['content']
def clean_output(res):
    res = res.replace("'", "")
    return res
def parse_narration(res):

    output = []
    spe = ""
    nar = ""
    mode = "speech"
    print(res)
    for c in res:
        if c == "(":
            if mode != "narrate":
                mode = "narrate"
                nar = ""
                if len(spe) > 0:
                    output.append("S:" + spe)
                    spe = ""
            continue
        if c == ")":
            mode = "speech"
            output.append("N:"+ nar)
            nar = ""
            continue
        if mode == "speech":
            spe += c
        else:
            nar += c

    if len(spe) > 0:
        output.append("S:" + spe)
    if len(nar) > 0:
        output.append("N:" + nar)
    print(output)
    return output


def get_reply(prompt):
    global send
    send.append({"role": "user", "content": prompt}, )

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=send,
    )
    res = response['choices'][0]['message']['content']
    #res = clean_output(res)
    send.append({"role": "assistant", "content": res})
    print(res)
    output = parse_narration(res)
    if len(output) > 3:
        output = output[0:3]
    if len(send) >= 20:
        send = [send[0]] + [send[1]] + [send[2]] + send[-12:]
        print("Trunkating chat")
    #     assistant_summary, user_summary = summarize(send)
    #     send = [send[0]]
    #     send.append({"role": "user", "content": user_summary})
    #     send.append({"role": "assistant", "content": assistant_summary})
    #     print("newly summarized: ", send)
    #    print(res)
    return output


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=False, port=33)
