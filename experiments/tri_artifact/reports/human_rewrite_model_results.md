# Independent Human-Rewrite Model Results

This is the frozen post-human exploratory OOD evaluation. API errors and missing rows
count as failures; the analyzer rejects incomplete or duplicate 50-task inventories.

| Run | Gold | Human majority | Human actionable | Majority-gold | Unanimous-gold | Actionable core | Reject policy |
|---|---:|---:|---:|---:|---:|---:|---:|
| qwen_generic | 30/50 (60.0%) | 29/48 (60.4%) | 68.3% | 65.9% | 75.7% | 72.5% | 10.0% |
| qwen_cta | 45/50 (90.0%) | 43/48 (89.6%) | 92.7% | 93.2% | 97.3% | 97.5% | 60.0% |
| qwen_free | 44/50 (88.0%) | 40/48 (83.3%) | 80.5% | 88.6% | 86.5% | 85.0% | 100.0% |
| qwen_gated | 45/50 (90.0%) | 41/48 (85.4%) | 82.9% | 90.9% | 89.2% | 87.5% | 100.0% |
| glm_generic | 37/50 (74.0%) | 33/48 (68.8%) | 68.3% | 75.0% | 81.1% | 72.5% | 80.0% |
| glm_cta | 49/50 (98.0%) | 45/48 (93.8%) | 92.7% | 100.0% | 100.0% | 100.0% | 90.0% |
| glm_free | 46/50 (92.0%) | 40/48 (83.3%) | 80.5% | 90.9% | 89.2% | 90.0% | 100.0% |
| glm_gated | 47/50 (94.0%) | 41/48 (85.4%) | 82.9% | 93.2% | 91.9% | 92.5% | 100.0% |

## Gold slices

### qwen_generic

```json
{
  "slices": {
    "binding": {
      "anchored": {
        "n": 25,
        "correct": 6,
        "accuracy": 0.24
      },
      "dynamic": {
        "n": 25,
        "correct": 24,
        "accuracy": 0.96
      }
    },
    "explicitness": {
      "explicit": {
        "n": 30,
        "correct": 17,
        "accuracy": 0.5666666666666667
      },
      "implicit": {
        "n": 20,
        "correct": 13,
        "accuracy": 0.65
      }
    },
    "update": {
      "flip": {
        "n": 10,
        "correct": 5,
        "accuracy": 0.5
      },
      "invalidate": {
        "n": 10,
        "correct": 5,
        "accuracy": 0.5
      },
      "name_collision": {
        "n": 10,
        "correct": 5,
        "accuracy": 0.5
      },
      "remove": {
        "n": 10,
        "correct": 5,
        "accuracy": 0.5
      },
      "stable": {
        "n": 10,
        "correct": 10,
        "accuracy": 1.0
      }
    },
    "template": {
      "explicit_anchor-t1": {
        "n": 3,
        "correct": 1,
        "accuracy": 0.3333333333333333
      },
      "explicit_anchor-t2": {
        "n": 4,
        "correct": 1,
        "accuracy": 0.25
      },
      "explicit_anchor-t4": {
        "n": 5,
        "correct": 0,
        "accuracy": 0.0
      },
      "explicit_anchor-t5": {
        "n": 3,
        "correct": 1,
        "accuracy": 0.3333333333333333
      },
      "explicit_dynamic-t1": {
        "n": 1,
        "correct": 1,
        "accuracy": 1.0
      },
      "explicit_dynamic-t2": {
        "n": 2,
        "correct": 2,
        "accuracy": 1.0
      },
      "explicit_dynamic-t3": {
        "n": 2,
        "correct": 2,
        "accuracy": 1.0
      },
      "explicit_dynamic-t4": {
        "n": 4,
        "correct": 3,
        "accuracy": 0.75
      },
      "explicit_dynamic-t5": {
        "n": 6,
        "correct": 6,
        "accuracy": 1.0
      },
      "implicit_anchor-t2": {
        "n": 2,
        "correct": 1,
        "accuracy": 0.5
      },
      "implicit_anchor-t3": {
        "n": 2,
        "correct": 0,
        "accuracy": 0.0
      },
      "implicit_anchor-t4": {
        "n": 4,
        "correct": 2,
        "accuracy": 0.5
      },
      "implicit_anchor-t5": {
        "n": 2,
        "correct": 0,
        "accuracy": 0.0
      },
      "implicit_dynamic-t1": {
        "n": 4,
        "correct": 4,
        "accuracy": 1.0
      },
      "implicit_dynamic-t2": {
        "n": 1,
        "correct": 1,
        "accuracy": 1.0
      },
      "implicit_dynamic-t3": {
        "n": 2,
        "correct": 2,
        "accuracy": 1.0
      },
      "implicit_dynamic-t4": {
        "n": 1,
        "correct": 1,
        "accuracy": 1.0
      },
      "implicit_dynamic-t5": {
        "n": 2,
        "correct": 2,
        "accuracy": 1.0
      }
    }
  },
  "errors": {
    "wrong_target_attempt": 18,
    "unnecessary_rejection": 2,
    "drift_to_new_leader": 9
  },
  "statuses": {
    "ok": 50
  },
  "api_retries": 0
}
```

### qwen_cta

```json
{
  "slices": {
    "binding": {
      "anchored": {
        "n": 25,
        "correct": 21,
        "accuracy": 0.84
      },
      "dynamic": {
        "n": 25,
        "correct": 24,
        "accuracy": 0.96
      }
    },
    "explicitness": {
      "explicit": {
        "n": 30,
        "correct": 28,
        "accuracy": 0.9333333333333333
      },
      "implicit": {
        "n": 20,
        "correct": 17,
        "accuracy": 0.85
      }
    },
    "update": {
      "flip": {
        "n": 10,
        "correct": 10,
        "accuracy": 1.0
      },
      "invalidate": {
        "n": 10,
        "correct": 6,
        "accuracy": 0.6
      },
      "name_collision": {
        "n": 10,
        "correct": 10,
        "accuracy": 1.0
      },
      "remove": {
        "n": 10,
        "correct": 9,
        "accuracy": 0.9
      },
      "stable": {
        "n": 10,
        "correct": 10,
        "accuracy": 1.0
      }
    },
    "template": {
      "explicit_anchor-t1": {
        "n": 3,
        "correct": 2,
        "accuracy": 0.6666666666666666
      },
      "explicit_anchor-t2": {
        "n": 4,
        "correct": 3,
        "accuracy": 0.75
      },
      "explicit_anchor-t4": {
        "n": 5,
        "correct": 5,
        "accuracy": 1.0
      },
      "explicit_anchor-t5": {
        "n": 3,
        "correct": 3,
        "accuracy": 1.0
      },
      "explicit_dynamic-t1": {
        "n": 1,
        "correct": 1,
        "accuracy": 1.0
      },
      "explicit_dynamic-t2": {
        "n": 2,
        "correct": 2,
        "accuracy": 1.0
      },
      "explicit_dynamic-t3": {
        "n": 2,
        "correct": 2,
        "accuracy": 1.0
      },
      "explicit_dynamic-t4": {
        "n": 4,
        "correct": 4,
        "accuracy": 1.0
      },
      "explicit_dynamic-t5": {
        "n": 6,
        "correct": 6,
        "accuracy": 1.0
      },
      "implicit_anchor-t2": {
        "n": 2,
        "correct": 2,
        "accuracy": 1.0
      },
      "implicit_anchor-t3": {
        "n": 2,
        "correct": 2,
        "accuracy": 1.0
      },
      "implicit_anchor-t4": {
        "n": 4,
        "correct": 3,
        "accuracy": 0.75
      },
      "implicit_anchor-t5": {
        "n": 2,
        "correct": 1,
        "accuracy": 0.5
      },
      "implicit_dynamic-t1": {
        "n": 4,
        "correct": 3,
        "accuracy": 0.75
      },
      "implicit_dynamic-t2": {
        "n": 1,
        "correct": 1,
        "accuracy": 1.0
      },
      "implicit_dynamic-t3": {
        "n": 2,
        "correct": 2,
        "accuracy": 1.0
      },
      "implicit_dynamic-t4": {
        "n": 1,
        "correct": 1,
        "accuracy": 1.0
      },
      "implicit_dynamic-t5": {
        "n": 2,
        "correct": 2,
        "accuracy": 1.0
      }
    }
  },
  "errors": {
    "wrong_target_attempt": 4,
    "invalid_target_attempt": 4,
    "unnecessary_rejection": 1
  },
  "statuses": {
    "ok": 50
  },
  "api_retries": 0
}
```

### qwen_free

```json
{
  "slices": {
    "binding": {
      "anchored": {
        "n": 25,
        "correct": 24,
        "accuracy": 0.96
      },
      "dynamic": {
        "n": 25,
        "correct": 20,
        "accuracy": 0.8
      }
    },
    "explicitness": {
      "explicit": {
        "n": 30,
        "correct": 27,
        "accuracy": 0.9
      },
      "implicit": {
        "n": 20,
        "correct": 17,
        "accuracy": 0.85
      }
    },
    "update": {
      "flip": {
        "n": 10,
        "correct": 7,
        "accuracy": 0.7
      },
      "invalidate": {
        "n": 10,
        "correct": 9,
        "accuracy": 0.9
      },
      "name_collision": {
        "n": 10,
        "correct": 9,
        "accuracy": 0.9
      },
      "remove": {
        "n": 10,
        "correct": 9,
        "accuracy": 0.9
      },
      "stable": {
        "n": 10,
        "correct": 10,
        "accuracy": 1.0
      }
    },
    "template": {
      "explicit_anchor-t1": {
        "n": 3,
        "correct": 3,
        "accuracy": 1.0
      },
      "explicit_anchor-t2": {
        "n": 4,
        "correct": 3,
        "accuracy": 0.75
      },
      "explicit_anchor-t4": {
        "n": 5,
        "correct": 5,
        "accuracy": 1.0
      },
      "explicit_anchor-t5": {
        "n": 3,
        "correct": 3,
        "accuracy": 1.0
      },
      "explicit_dynamic-t1": {
        "n": 1,
        "correct": 1,
        "accuracy": 1.0
      },
      "explicit_dynamic-t2": {
        "n": 2,
        "correct": 1,
        "accuracy": 0.5
      },
      "explicit_dynamic-t3": {
        "n": 2,
        "correct": 2,
        "accuracy": 1.0
      },
      "explicit_dynamic-t4": {
        "n": 4,
        "correct": 4,
        "accuracy": 1.0
      },
      "explicit_dynamic-t5": {
        "n": 6,
        "correct": 5,
        "accuracy": 0.8333333333333334
      },
      "implicit_anchor-t2": {
        "n": 2,
        "correct": 2,
        "accuracy": 1.0
      },
      "implicit_anchor-t3": {
        "n": 2,
        "correct": 2,
        "accuracy": 1.0
      },
      "implicit_anchor-t4": {
        "n": 4,
        "correct": 4,
        "accuracy": 1.0
      },
      "implicit_anchor-t5": {
        "n": 2,
        "correct": 2,
        "accuracy": 1.0
      },
      "implicit_dynamic-t1": {
        "n": 4,
        "correct": 2,
        "accuracy": 0.5
      },
      "implicit_dynamic-t2": {
        "n": 1,
        "correct": 0,
        "accuracy": 0.0
      },
      "implicit_dynamic-t3": {
        "n": 2,
        "correct": 2,
        "accuracy": 1.0
      },
      "implicit_dynamic-t4": {
        "n": 1,
        "correct": 1,
        "accuracy": 1.0
      },
      "implicit_dynamic-t5": {
        "n": 2,
        "correct": 2,
        "accuracy": 1.0
      }
    }
  },
  "errors": {
    "unnecessary_rejection": 3,
    "wrong_target_attempt": 3
  },
  "statuses": {
    "ok": 50
  },
  "api_retries": 0
}
```

### qwen_gated

```json
{
  "slices": {
    "binding": {
      "anchored": {
        "n": 25,
        "correct": 25,
        "accuracy": 1.0
      },
      "dynamic": {
        "n": 25,
        "correct": 20,
        "accuracy": 0.8
      }
    },
    "explicitness": {
      "explicit": {
        "n": 30,
        "correct": 28,
        "accuracy": 0.9333333333333333
      },
      "implicit": {
        "n": 20,
        "correct": 17,
        "accuracy": 0.85
      }
    },
    "update": {
      "flip": {
        "n": 10,
        "correct": 8,
        "accuracy": 0.8
      },
      "invalidate": {
        "n": 10,
        "correct": 9,
        "accuracy": 0.9
      },
      "name_collision": {
        "n": 10,
        "correct": 9,
        "accuracy": 0.9
      },
      "remove": {
        "n": 10,
        "correct": 9,
        "accuracy": 0.9
      },
      "stable": {
        "n": 10,
        "correct": 10,
        "accuracy": 1.0
      }
    },
    "template": {
      "explicit_anchor-t1": {
        "n": 3,
        "correct": 3,
        "accuracy": 1.0
      },
      "explicit_anchor-t2": {
        "n": 4,
        "correct": 4,
        "accuracy": 1.0
      },
      "explicit_anchor-t4": {
        "n": 5,
        "correct": 5,
        "accuracy": 1.0
      },
      "explicit_anchor-t5": {
        "n": 3,
        "correct": 3,
        "accuracy": 1.0
      },
      "explicit_dynamic-t1": {
        "n": 1,
        "correct": 1,
        "accuracy": 1.0
      },
      "explicit_dynamic-t2": {
        "n": 2,
        "correct": 1,
        "accuracy": 0.5
      },
      "explicit_dynamic-t3": {
        "n": 2,
        "correct": 2,
        "accuracy": 1.0
      },
      "explicit_dynamic-t4": {
        "n": 4,
        "correct": 4,
        "accuracy": 1.0
      },
      "explicit_dynamic-t5": {
        "n": 6,
        "correct": 5,
        "accuracy": 0.8333333333333334
      },
      "implicit_anchor-t2": {
        "n": 2,
        "correct": 2,
        "accuracy": 1.0
      },
      "implicit_anchor-t3": {
        "n": 2,
        "correct": 2,
        "accuracy": 1.0
      },
      "implicit_anchor-t4": {
        "n": 4,
        "correct": 4,
        "accuracy": 1.0
      },
      "implicit_anchor-t5": {
        "n": 2,
        "correct": 2,
        "accuracy": 1.0
      },
      "implicit_dynamic-t1": {
        "n": 4,
        "correct": 2,
        "accuracy": 0.5
      },
      "implicit_dynamic-t2": {
        "n": 1,
        "correct": 0,
        "accuracy": 0.0
      },
      "implicit_dynamic-t3": {
        "n": 2,
        "correct": 2,
        "accuracy": 1.0
      },
      "implicit_dynamic-t4": {
        "n": 1,
        "correct": 1,
        "accuracy": 1.0
      },
      "implicit_dynamic-t5": {
        "n": 2,
        "correct": 2,
        "accuracy": 1.0
      }
    }
  },
  "errors": {
    "unnecessary_rejection": 2,
    "wrong_target_attempt": 3
  },
  "statuses": {
    "ok": 50
  },
  "api_retries": 0
}
```

### glm_generic

```json
{
  "slices": {
    "binding": {
      "anchored": {
        "n": 25,
        "correct": 13,
        "accuracy": 0.52
      },
      "dynamic": {
        "n": 25,
        "correct": 24,
        "accuracy": 0.96
      }
    },
    "explicitness": {
      "explicit": {
        "n": 30,
        "correct": 21,
        "accuracy": 0.7
      },
      "implicit": {
        "n": 20,
        "correct": 16,
        "accuracy": 0.8
      }
    },
    "update": {
      "flip": {
        "n": 10,
        "correct": 4,
        "accuracy": 0.4
      },
      "invalidate": {
        "n": 10,
        "correct": 10,
        "accuracy": 1.0
      },
      "name_collision": {
        "n": 10,
        "correct": 5,
        "accuracy": 0.5
      },
      "remove": {
        "n": 10,
        "correct": 8,
        "accuracy": 0.8
      },
      "stable": {
        "n": 10,
        "correct": 10,
        "accuracy": 1.0
      }
    },
    "template": {
      "explicit_anchor-t1": {
        "n": 3,
        "correct": 3,
        "accuracy": 1.0
      },
      "explicit_anchor-t2": {
        "n": 4,
        "correct": 2,
        "accuracy": 0.5
      },
      "explicit_anchor-t4": {
        "n": 5,
        "correct": 1,
        "accuracy": 0.2
      },
      "explicit_anchor-t5": {
        "n": 3,
        "correct": 1,
        "accuracy": 0.3333333333333333
      },
      "explicit_dynamic-t1": {
        "n": 1,
        "correct": 1,
        "accuracy": 1.0
      },
      "explicit_dynamic-t2": {
        "n": 2,
        "correct": 2,
        "accuracy": 1.0
      },
      "explicit_dynamic-t3": {
        "n": 2,
        "correct": 2,
        "accuracy": 1.0
      },
      "explicit_dynamic-t4": {
        "n": 4,
        "correct": 4,
        "accuracy": 1.0
      },
      "explicit_dynamic-t5": {
        "n": 6,
        "correct": 5,
        "accuracy": 0.8333333333333334
      },
      "implicit_anchor-t2": {
        "n": 2,
        "correct": 1,
        "accuracy": 0.5
      },
      "implicit_anchor-t3": {
        "n": 2,
        "correct": 0,
        "accuracy": 0.0
      },
      "implicit_anchor-t4": {
        "n": 4,
        "correct": 3,
        "accuracy": 0.75
      },
      "implicit_anchor-t5": {
        "n": 2,
        "correct": 2,
        "accuracy": 1.0
      },
      "implicit_dynamic-t1": {
        "n": 4,
        "correct": 4,
        "accuracy": 1.0
      },
      "implicit_dynamic-t2": {
        "n": 1,
        "correct": 1,
        "accuracy": 1.0
      },
      "implicit_dynamic-t3": {
        "n": 2,
        "correct": 2,
        "accuracy": 1.0
      },
      "implicit_dynamic-t4": {
        "n": 1,
        "correct": 1,
        "accuracy": 1.0
      },
      "implicit_dynamic-t5": {
        "n": 2,
        "correct": 2,
        "accuracy": 1.0
      }
    }
  },
  "errors": {
    "wrong_target_attempt": 6,
    "drift_to_new_leader": 4,
    "unnecessary_rejection": 7
  },
  "statuses": {
    "ok": 50
  },
  "api_retries": 0
}
```

### glm_cta

```json
{
  "slices": {
    "binding": {
      "anchored": {
        "n": 25,
        "correct": 24,
        "accuracy": 0.96
      },
      "dynamic": {
        "n": 25,
        "correct": 25,
        "accuracy": 1.0
      }
    },
    "explicitness": {
      "explicit": {
        "n": 30,
        "correct": 30,
        "accuracy": 1.0
      },
      "implicit": {
        "n": 20,
        "correct": 19,
        "accuracy": 0.95
      }
    },
    "update": {
      "flip": {
        "n": 10,
        "correct": 10,
        "accuracy": 1.0
      },
      "invalidate": {
        "n": 10,
        "correct": 9,
        "accuracy": 0.9
      },
      "name_collision": {
        "n": 10,
        "correct": 10,
        "accuracy": 1.0
      },
      "remove": {
        "n": 10,
        "correct": 10,
        "accuracy": 1.0
      },
      "stable": {
        "n": 10,
        "correct": 10,
        "accuracy": 1.0
      }
    },
    "template": {
      "explicit_anchor-t1": {
        "n": 3,
        "correct": 3,
        "accuracy": 1.0
      },
      "explicit_anchor-t2": {
        "n": 4,
        "correct": 4,
        "accuracy": 1.0
      },
      "explicit_anchor-t4": {
        "n": 5,
        "correct": 5,
        "accuracy": 1.0
      },
      "explicit_anchor-t5": {
        "n": 3,
        "correct": 3,
        "accuracy": 1.0
      },
      "explicit_dynamic-t1": {
        "n": 1,
        "correct": 1,
        "accuracy": 1.0
      },
      "explicit_dynamic-t2": {
        "n": 2,
        "correct": 2,
        "accuracy": 1.0
      },
      "explicit_dynamic-t3": {
        "n": 2,
        "correct": 2,
        "accuracy": 1.0
      },
      "explicit_dynamic-t4": {
        "n": 4,
        "correct": 4,
        "accuracy": 1.0
      },
      "explicit_dynamic-t5": {
        "n": 6,
        "correct": 6,
        "accuracy": 1.0
      },
      "implicit_anchor-t2": {
        "n": 2,
        "correct": 2,
        "accuracy": 1.0
      },
      "implicit_anchor-t3": {
        "n": 2,
        "correct": 2,
        "accuracy": 1.0
      },
      "implicit_anchor-t4": {
        "n": 4,
        "correct": 3,
        "accuracy": 0.75
      },
      "implicit_anchor-t5": {
        "n": 2,
        "correct": 2,
        "accuracy": 1.0
      },
      "implicit_dynamic-t1": {
        "n": 4,
        "correct": 4,
        "accuracy": 1.0
      },
      "implicit_dynamic-t2": {
        "n": 1,
        "correct": 1,
        "accuracy": 1.0
      },
      "implicit_dynamic-t3": {
        "n": 2,
        "correct": 2,
        "accuracy": 1.0
      },
      "implicit_dynamic-t4": {
        "n": 1,
        "correct": 1,
        "accuracy": 1.0
      },
      "implicit_dynamic-t5": {
        "n": 2,
        "correct": 2,
        "accuracy": 1.0
      }
    }
  },
  "errors": {
    "wrong_target_attempt": 1,
    "invalid_target_attempt": 1
  },
  "statuses": {
    "ok": 50
  },
  "api_retries": 0
}
```

### glm_free

```json
{
  "slices": {
    "binding": {
      "anchored": {
        "n": 25,
        "correct": 24,
        "accuracy": 0.96
      },
      "dynamic": {
        "n": 25,
        "correct": 22,
        "accuracy": 0.88
      }
    },
    "explicitness": {
      "explicit": {
        "n": 30,
        "correct": 26,
        "accuracy": 0.8666666666666667
      },
      "implicit": {
        "n": 20,
        "correct": 20,
        "accuracy": 1.0
      }
    },
    "update": {
      "flip": {
        "n": 10,
        "correct": 9,
        "accuracy": 0.9
      },
      "invalidate": {
        "n": 10,
        "correct": 9,
        "accuracy": 0.9
      },
      "name_collision": {
        "n": 10,
        "correct": 9,
        "accuracy": 0.9
      },
      "remove": {
        "n": 10,
        "correct": 9,
        "accuracy": 0.9
      },
      "stable": {
        "n": 10,
        "correct": 10,
        "accuracy": 1.0
      }
    },
    "template": {
      "explicit_anchor-t1": {
        "n": 3,
        "correct": 3,
        "accuracy": 1.0
      },
      "explicit_anchor-t2": {
        "n": 4,
        "correct": 4,
        "accuracy": 1.0
      },
      "explicit_anchor-t4": {
        "n": 5,
        "correct": 4,
        "accuracy": 0.8
      },
      "explicit_anchor-t5": {
        "n": 3,
        "correct": 3,
        "accuracy": 1.0
      },
      "explicit_dynamic-t1": {
        "n": 1,
        "correct": 1,
        "accuracy": 1.0
      },
      "explicit_dynamic-t2": {
        "n": 2,
        "correct": 0,
        "accuracy": 0.0
      },
      "explicit_dynamic-t3": {
        "n": 2,
        "correct": 2,
        "accuracy": 1.0
      },
      "explicit_dynamic-t4": {
        "n": 4,
        "correct": 4,
        "accuracy": 1.0
      },
      "explicit_dynamic-t5": {
        "n": 6,
        "correct": 5,
        "accuracy": 0.8333333333333334
      },
      "implicit_anchor-t2": {
        "n": 2,
        "correct": 2,
        "accuracy": 1.0
      },
      "implicit_anchor-t3": {
        "n": 2,
        "correct": 2,
        "accuracy": 1.0
      },
      "implicit_anchor-t4": {
        "n": 4,
        "correct": 4,
        "accuracy": 1.0
      },
      "implicit_anchor-t5": {
        "n": 2,
        "correct": 2,
        "accuracy": 1.0
      },
      "implicit_dynamic-t1": {
        "n": 4,
        "correct": 4,
        "accuracy": 1.0
      },
      "implicit_dynamic-t2": {
        "n": 1,
        "correct": 1,
        "accuracy": 1.0
      },
      "implicit_dynamic-t3": {
        "n": 2,
        "correct": 2,
        "accuracy": 1.0
      },
      "implicit_dynamic-t4": {
        "n": 1,
        "correct": 1,
        "accuracy": 1.0
      },
      "implicit_dynamic-t5": {
        "n": 2,
        "correct": 2,
        "accuracy": 1.0
      }
    }
  },
  "errors": {
    "unnecessary_rejection": 3,
    "wrong_target_attempt": 1
  },
  "statuses": {
    "ok": 50
  },
  "api_retries": 0
}
```

### glm_gated

```json
{
  "slices": {
    "binding": {
      "anchored": {
        "n": 25,
        "correct": 25,
        "accuracy": 1.0
      },
      "dynamic": {
        "n": 25,
        "correct": 22,
        "accuracy": 0.88
      }
    },
    "explicitness": {
      "explicit": {
        "n": 30,
        "correct": 27,
        "accuracy": 0.9
      },
      "implicit": {
        "n": 20,
        "correct": 20,
        "accuracy": 1.0
      }
    },
    "update": {
      "flip": {
        "n": 10,
        "correct": 9,
        "accuracy": 0.9
      },
      "invalidate": {
        "n": 10,
        "correct": 9,
        "accuracy": 0.9
      },
      "name_collision": {
        "n": 10,
        "correct": 10,
        "accuracy": 1.0
      },
      "remove": {
        "n": 10,
        "correct": 9,
        "accuracy": 0.9
      },
      "stable": {
        "n": 10,
        "correct": 10,
        "accuracy": 1.0
      }
    },
    "template": {
      "explicit_anchor-t1": {
        "n": 3,
        "correct": 3,
        "accuracy": 1.0
      },
      "explicit_anchor-t2": {
        "n": 4,
        "correct": 4,
        "accuracy": 1.0
      },
      "explicit_anchor-t4": {
        "n": 5,
        "correct": 5,
        "accuracy": 1.0
      },
      "explicit_anchor-t5": {
        "n": 3,
        "correct": 3,
        "accuracy": 1.0
      },
      "explicit_dynamic-t1": {
        "n": 1,
        "correct": 1,
        "accuracy": 1.0
      },
      "explicit_dynamic-t2": {
        "n": 2,
        "correct": 0,
        "accuracy": 0.0
      },
      "explicit_dynamic-t3": {
        "n": 2,
        "correct": 2,
        "accuracy": 1.0
      },
      "explicit_dynamic-t4": {
        "n": 4,
        "correct": 4,
        "accuracy": 1.0
      },
      "explicit_dynamic-t5": {
        "n": 6,
        "correct": 5,
        "accuracy": 0.8333333333333334
      },
      "implicit_anchor-t2": {
        "n": 2,
        "correct": 2,
        "accuracy": 1.0
      },
      "implicit_anchor-t3": {
        "n": 2,
        "correct": 2,
        "accuracy": 1.0
      },
      "implicit_anchor-t4": {
        "n": 4,
        "correct": 4,
        "accuracy": 1.0
      },
      "implicit_anchor-t5": {
        "n": 2,
        "correct": 2,
        "accuracy": 1.0
      },
      "implicit_dynamic-t1": {
        "n": 4,
        "correct": 4,
        "accuracy": 1.0
      },
      "implicit_dynamic-t2": {
        "n": 1,
        "correct": 1,
        "accuracy": 1.0
      },
      "implicit_dynamic-t3": {
        "n": 2,
        "correct": 2,
        "accuracy": 1.0
      },
      "implicit_dynamic-t4": {
        "n": 1,
        "correct": 1,
        "accuracy": 1.0
      },
      "implicit_dynamic-t5": {
        "n": 2,
        "correct": 2,
        "accuracy": 1.0
      }
    }
  },
  "errors": {
    "unnecessary_rejection": 2,
    "wrong_target_attempt": 1
  },
  "statuses": {
    "ok": 50
  },
  "api_retries": 0
}
```

## Paired cluster comparisons

```json
{
  "qwen_cta_minus_qwen_generic": {
    "difference": 0.3,
    "cluster_95_interval": [
      0.11320754716981132,
      0.5
    ],
    "n_clusters": 18,
    "samples": 10000,
    "seed": 20260719,
    "secondary_task_level_mcnemar": {
      "baseline_only": 1,
      "treatment_only": 16,
      "exact_mcnemar_p": 0.000274658203125
    }
  },
  "qwen_free_minus_qwen_generic": {
    "difference": 0.28,
    "cluster_95_interval": [
      0.02127659574468085,
      0.5283018867924528
    ],
    "n_clusters": 18,
    "samples": 10000,
    "seed": 20260719,
    "secondary_task_level_mcnemar": {
      "baseline_only": 5,
      "treatment_only": 19,
      "exact_mcnemar_p": 0.006610751152038574
    }
  },
  "qwen_gated_minus_qwen_generic": {
    "difference": 0.3,
    "cluster_95_interval": [
      0.037037037037037035,
      0.5555555555555556
    ],
    "n_clusters": 18,
    "samples": 10000,
    "seed": 20260719,
    "secondary_task_level_mcnemar": {
      "baseline_only": 5,
      "treatment_only": 20,
      "exact_mcnemar_p": 0.004077315330505371
    }
  },
  "qwen_cta_minus_qwen_free": {
    "difference": 0.02,
    "cluster_95_interval": [
      -0.0851063829787234,
      0.12195121951219512
    ],
    "n_clusters": 18,
    "samples": 10000,
    "seed": 20260719,
    "secondary_task_level_mcnemar": {
      "baseline_only": 5,
      "treatment_only": 6,
      "exact_mcnemar_p": 1.0
    }
  },
  "qwen_cta_minus_qwen_gated": {
    "difference": 0.0,
    "cluster_95_interval": [
      -0.1111111111111111,
      0.1111111111111111
    ],
    "n_clusters": 18,
    "samples": 10000,
    "seed": 20260719,
    "secondary_task_level_mcnemar": {
      "baseline_only": 5,
      "treatment_only": 5,
      "exact_mcnemar_p": 1.0
    }
  },
  "glm_cta_minus_glm_generic": {
    "difference": 0.24,
    "cluster_95_interval": [
      0.08333333333333333,
      0.41304347826086957
    ],
    "n_clusters": 18,
    "samples": 10000,
    "seed": 20260719,
    "secondary_task_level_mcnemar": {
      "baseline_only": 1,
      "treatment_only": 13,
      "exact_mcnemar_p": 0.0018310546875
    }
  },
  "glm_free_minus_glm_generic": {
    "difference": 0.18,
    "cluster_95_interval": [
      0.0,
      0.35185185185185186
    ],
    "n_clusters": 18,
    "samples": 10000,
    "seed": 20260719,
    "secondary_task_level_mcnemar": {
      "baseline_only": 2,
      "treatment_only": 11,
      "exact_mcnemar_p": 0.0224609375
    }
  },
  "glm_gated_minus_glm_generic": {
    "difference": 0.2,
    "cluster_95_interval": [
      0.0,
      0.39215686274509803
    ],
    "n_clusters": 18,
    "samples": 10000,
    "seed": 20260719,
    "secondary_task_level_mcnemar": {
      "baseline_only": 2,
      "treatment_only": 12,
      "exact_mcnemar_p": 0.012939453125
    }
  },
  "glm_cta_minus_glm_free": {
    "difference": 0.06,
    "cluster_95_interval": [
      -0.03571428571428571,
      0.16666666666666666
    ],
    "n_clusters": 18,
    "samples": 10000,
    "seed": 20260719,
    "secondary_task_level_mcnemar": {
      "baseline_only": 1,
      "treatment_only": 4,
      "exact_mcnemar_p": 0.375
    }
  },
  "glm_cta_minus_glm_gated": {
    "difference": 0.04,
    "cluster_95_interval": [
      -0.043478260869565216,
      0.14814814814814814
    ],
    "n_clusters": 18,
    "samples": 10000,
    "seed": 20260719,
    "secondary_task_level_mcnemar": {
      "baseline_only": 1,
      "treatment_only": 3,
      "exact_mcnemar_p": 0.625
    }
  }
}
```
