package com.clinical.summarizer.repository;

import com.clinical.summarizer.model.PatientCase;
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface PatientCaseRepository extends MongoRepository<PatientCase, String> {
    List<PatientCase> findByPatientAge(String age);
    List<PatientCase> findByGender(String gender);
}
