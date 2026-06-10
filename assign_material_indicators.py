import clr
import os
import uuid
import System

clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')

from Autodesk.Revit.DB import *
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

def flatten(lst):
    result = []
    for item in lst:
        if isinstance(item, (list, tuple)):
            result.extend(flatten(item))
        else:
            result.append(item)
    return result

def guid_per_codice(nome):
    NAMESPACE = uuid.UUID("12345678-1234-5678-1234-567812345678")
    return str(uuid.uuid5(NAMESPACE, nome)).upper()

def converti(v):
    try:
        return float(str(v).replace(",", "."))
    except:
        return 0.0

try:
    material = UnwrapElement(IN[0])
    codici   = [str(c).strip() for c in flatten(IN[1])]
    valori   = flatten(IN[2])

    doc = DocumentManager.Instance.CurrentDBDocument
    app = doc.Application

    risultati = []
    errori    = []

    parametri_mancanti = []
    for codice in codici:
        trovato = False
        it = doc.ParameterBindings.ForwardIterator()
        while it.MoveNext():
            if it.Key.Name == codice:
                trovato = True
                break
        if not trovato:
            parametri_mancanti.append(codice)

    if len(parametri_mancanti) > 0:

        sp_path = r"C:\Temp\LC_SharedParams.txt"
        if not os.path.exists(r"C:\Temp"):
            os.makedirs(r"C:\Temp")

        with open(sp_path, "w") as f:
            f.write("# This is a Revit shared parameter file.\n")
            f.write("# Do not edit manually.\n")
            f.write("*META\tVERSION\tMINVERSION\n")
            f.write("META\t2\t1\n")
            f.write("*GROUP\tID\tNAME\n")
            f.write("GROUP\t1\tIndicatori LC\n")
            f.write("*PARAM\tGUID\tNAME\tDATATYPE\tDATACATEGORY\tGROUP\tVISIBLE\n")
            for codice in codici:
                g = guid_per_codice(codice)
                f.write("PARAM\t{" + g + "}\t" + codice + "\tNUMBER\t\t1\t1\n")

        app.SharedParametersFilename = ""
        app.SharedParametersFilename = sp_path
        sp_file = app.OpenSharedParameterFile()

        sp_group = None
        for g in sp_file.Groups:
            if g.Name == "Indicatori LC":
                sp_group = g
                break
        if sp_group is None:
            sp_group = sp_file.Groups.Create("Indicatori LC")

        cat_set = CategorySet()
        cat_set.Insert(doc.Settings.Categories.get_Item(BuiltInCategory.OST_Materials))

        for codice in parametri_mancanti:
            try:
                ext_def = None
                for d in sp_group.Definitions:
                    if d.Name == codice:
                        ext_def = d
                        break

                if ext_def is None:
                    opt = ExternalDefinitionCreationOptions(codice, SpecTypeId.Number)
                    opt.GUID = System.Guid(guid_per_codice(codice).lower())
                    opt.Visible = True
                    ext_def = sp_group.Definitions.Create(opt)

                binding_new = app.Create.NewInstanceBinding(cat_set)

                TransactionManager.Instance.EnsureInTransaction(doc)
                doc.ParameterBindings.Insert(ext_def, binding_new, GroupTypeId.Data)
                TransactionManager.Instance.TransactionTaskDone()
                doc.Regenerate()

                risultati.append("CREATO: " + codice)

            except Exception as e:
                try:
                    TransactionManager.Instance.TransactionTaskDone()
                except:
                    pass
                errori.append("ERR BINDING: " + codice + " - " + str(e))

    TransactionManager.Instance.EnsureInTransaction(doc)

    for i, codice in enumerate(codici):
        valore = valori[i]
        try:
            param = material.LookupParameter(codice)
            if param is None:
                errori.append("NO PARAM: " + codice)
                continue
            if param.IsReadOnly:
                errori.append("READ ONLY: " + codice)
                continue
            storage = param.StorageType
            if storage == StorageType.Double:
                param.Set(converti(valore))
            elif storage == StorageType.Integer:
                param.Set(int(converti(valore)))
            else:
                param.SetValueString(str(valore))
            risultati.append("OK: " + codice + " = " + str(valore))
        except Exception as e:
            errori.append("VALORE ERR: " + codice + " - " + str(e))

    TransactionManager.Instance.TransactionTaskDone()

    OUT = risultati, errori

except Exception as e:
    OUT = [], ["CRASH: " + str(e)]
