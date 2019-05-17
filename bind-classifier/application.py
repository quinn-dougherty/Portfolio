''' Application to serve on Elastic Beanstalk.  '''
from flask import Flask, request, jsonify
import json
from script import predict, lig_tfidf
application = app = Flask(__name__)

@app.route("/", methods=['POST'])   #<ligid>/<seqid>", methods=['POST']
def get():
    lines = request.get_json(force=True)
    ligid = lines['ligid'] # keys in file test_json_get.py
    seqid = lines['seqid']

    outdat = {'ligid': ligid, 'seqid': seqid, 'prediction': str(predict(ligid, seqid))}
    
    outdat = {'key1': int1, 'key2': int2}
    
    response = app.response_class(
            response=json.dumps(outdat), 
            status=200, 
            mimetype='application/json', 
            header
            )

    return response

if __name__=='__main__': 
    app.run(debug=True)
