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
    "id": "phv00180619.v1.p1",
    "description": "subject's percentile on color trails test 1 form a (d'elia et. al.)",
    "same_concepts": [],
    "new_concepts": [
      {
        "id": "UMLS:C1264641",
        "norm_id": "UMLS:C1264641",
        "label": "Percentile",
        "description": ""
      },
      {
        "id": "UMLS:C1532337",
        "norm_id": "UMLS:C1532337",
        "label": "Percentile value",
        "description": ""
      },
      {
        "id": "UMLS:C0449570",
        "norm_id": "UMLS:C0449570",
        "label": "Test type",
        "description": ""
      },
      {
        "id": "UMLS:C2826273",
        "norm_id": "UMLS:C2826273",
        "label": "Test Name",
        "description": ""
      }
    ],
    "deleted_concepts": [
      {
        "id": "PR:000002106",
        "norm_id": "PR:000002106",
        "label": "tumor necrosis factor ligand superfamily member 10",
        "description": "A tumor necrosis factor ligand superfamily member 10/11 that is a translation product of the human TNFSF10 gene or a 1:1 ortholog thereof."
      }
    ]
  },
```
