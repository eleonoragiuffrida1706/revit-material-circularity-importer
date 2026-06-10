# Revit Material Circularity Importer

Python script for Autodesk Revit and Dynamo that automatically creates Shared Parameters and assigns circularity indicator values to BIM materials.

## Overview

The script supports the integration of circularity assessment results into BIM models by transferring indicator values to Revit material parameters.

The workflow enables sustainability information to become part of the BIM model, allowing designers and stakeholders to access circularity-related data directly within the Revit environment.

## Features

* Automatic creation of Shared Parameters.
* Automatic parameter binding to Revit Materials.
* Deterministic GUID generation for parameter consistency.
* Automatic writing of indicator values.
* Error handling and execution reporting.

## Dynamo Inputs

| Input | Description              |
| ----- | ------------------------ |
| IN[0] | Revit Material           |
| IN[1] | List of indicator codes  |
| IN[2] | List of indicator values |

## Dynamo Outputs

| Output | Description       |
| ------ | ----------------- |
| OUT[0] | Execution results |
| OUT[1] | Error messages    |

## Requirements

* Autodesk Revit
* Dynamo
* Revit API
* RevitServices

## Example Workflow

1. Circularity indicators are calculated externally.
2. Dynamo reads indicator codes and values.
3. The script creates missing Shared Parameters.
4. The script binds parameters to Revit Materials.
5. The script writes indicator values into material properties.

## License

MIT License.
