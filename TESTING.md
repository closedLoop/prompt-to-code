# TESTING

## Human Eval Dataset

To run testing on the human eval dataset, run the following command:


```bash
python examples/human_eval_script.py
```

If there are errors, please follow them and install the missing dependencies.


### Test Results

Using the human eval dataset, we were able to achieve the following results:

Agents:
* basic: Only one call to the language model was made for each problem
* reflection: Two calls were made to the language model for each problem
* tdd: One Red-Green-Refactor loop was performed for each problem

Temperatures: 0.2, 0.7
num samples per question: 5

Number of questions = 167
Number of samples = 5010
Estimated cost to run = $1,323

Params:
    Agent = 'tdd'
    model = 'OpenAIChat'
    model_name = 'gpt-4'
    temperature = 0.2

Results:
    pass@1 = 0.93%
    pass@2 = 0.93%
    pass@3 = 0.93%
    ....

    Calculation Time = 0.0
    Cost = 0.0

    Accuracy = 0.0
    Precision = 0.0
    Recall = 0.0
    F1 = 0.0
