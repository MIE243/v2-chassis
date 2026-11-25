d = doc(r"C:\Users\M0obo\OneDrive\Desktop\MIE243\v1-chassis\Transfer Case\v1_TransferCase.SLDASM")
c = comps(d)
print(len(c), "comps;", len(mate_errors(d)), "mate errors", mate_errors(d)[:3])
print("unsaved:", bool(d.GetSaveFlag))
