# DugAnnotationComparator

To download dependencies:
```pip install -r requirements.txt```

**Example of usage if you need to get files from LakeFS:**

1) Create json file with parameters. You can find sample json file here: src/sample_task.json
2) ```python main.py -t ./anvil_main_dbgap.json```

**Example of usage if you have files locally:**

```python main.py -l "/path1/annotate_and_index/anvil" "/path2/annotate_and_index/anvil" -d ./output.json```

parameters:
```
-l - list of paths to annotation files`

-d - path of json output file`
```

example of an output:
```
...
 {
    "id": "phv00071849.v1.p1",
    "description": "if the subject does not meet criteria for dementia, what is the diagnosis?",
    "same_concepts": [],
    "new_concepts": [
      {
        "id": "UMLS:C0243161",
        "norm_id": "UMLS:C0243161",
        "label": "criteria"
      }
    ],
    "deleted_concepts": [
      {
        "id": "PUBCHEM.COMPOUND:6137",
        "norm_id": "CHEBI:16643",
        "label": "L-methionine"
      },
      {
        "id": "PUBCHEM.COMPOUND:876",
        "norm_id": "CHEBI:16811",
        "label": "methionine"
      },
      {
        "id": "NCBIGene:4233",
        "norm_id": "NCBIGene:4233",
        "label": "MET"
      },
      {
        "id": "PR:000010335",
        "norm_id": "PR:000010335",
        "label": "hepatocyte growth factor receptor"
      }
    ]
  }
```
