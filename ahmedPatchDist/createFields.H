const dictionary& schemesDict = static_cast<const fvSchemes&>(mesh).schemesDict();
const word wallDistMethod (schemesDict.subDict("wallDist").lookup("method"));
// const word saveName = "distAhmed"
Info << "wallDistMethod: " << wallDistMethod << endl;

//get the patchID, add to labelHashSet
label patchID = mesh.boundaryMesh().findPatchID("wallAhmed");
Info << "patchID: " << patchID << endl;

labelHashSet hashPatchID;
hashPatchID.insert(patchID);
wallDist ahmedDist (mesh, wallDistMethod, hashPatchID, "patch");

volScalarField distField = ahmedDist.y();
// distField.name = saveName;
Info<< "Writing wall distance to " << distField.name() << endl;
distField.write();