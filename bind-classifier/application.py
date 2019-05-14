''' attempting to do it not as RESTful ''' 
from flask import Flask, request, jsonify#, response_class
import json
#from script import predict, lig_tfidf
application = app = Flask(__name__)

@app.route("/", methods=['POST'])      #<ligid>/<seqid>", methods=['POST']
def get():
    lines = request.get_json(force=True)
    ligid = lines['int1'] # keys in file test_json_get.py 
    seqid = lines['int2']

    #thing = lig_tfidf.transform(["hey peyton how's austin"])

    #outdat = {'ligid': ligid, 'seqid': seqid, 'prediction': str(predict(ligid, seqid))}
    
    outdat = {'key1': int1, 'key2': int2}
    
    response = app.response_class(
            response=json.dumps(outdat), 
            status=200, 
            mimetype='application/json', 
            header
            )

    #response = Response(outdat, stat
    return response

if __name__=='__main__': 
    app.run(debug=True)

''' from flask import json

@app.route('/summary')
def summary():
    data = make_summary()
    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response ''' 
