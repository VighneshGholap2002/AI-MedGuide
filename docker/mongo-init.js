// This script runs during MongoDB initialization via mongosh
// The root admin user is already created from MONGO_INITDB_ROOT_USERNAME/PASSWORD
// Now we create the application database user

// Switch to admin database first to authenticate as root (if needed)
db = db.getSiblingDB("admin");

// Switch to the application database
db = db.getSiblingDB("clinical_summarizer");

// Try to create the user
try {
  db.createUser({
    user: "admin",
    pwd: "password",
    roles: [{ role: "dbOwner", db: "clinical_summarizer" }],
  });
  console.log("Created admin user for clinical_summarizer database");
} catch (e) {
  if (e.code === 48) {
    console.log("User admin already exists");
  } else {
    throw e;
  }
}

// Create patient_cases collection if it doesn't exist
try {
  db.createCollection("patient_cases");
  console.log("Created patient_cases collection");
} catch (e) {
  if (e.codeName === "NamespaceExists") {
    console.log("patient_cases collection already exists");
  } else {
    console.log("Error creating collection: " + e);
  }
}

// Create indexes
db.patient_cases.createIndex({ caseTitle: 1 });
db.patient_cases.createIndex({ patientAge: 1 });
console.log("Indexes created successfully");
