package com.clinical.summarizer.controller;

import com.clinical.summarizer.model.PatientCase;
import com.clinical.summarizer.service.SummarizationService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/v1/cases")
@RequiredArgsConstructor
@Slf4j
@CrossOrigin(origins = "http://localhost:3000")
public class PatientCaseController {

    private final SummarizationService summarizationService;

    @PostMapping
    public ResponseEntity<PatientCase> createCase(@RequestBody PatientCase patientCase) {
        log.info("Creating new patient case");
        PatientCase created = summarizationService.createCase(patientCase);
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }

    @GetMapping
    public ResponseEntity<List<PatientCase>> getAllCases() {
        log.info("Fetching all patient cases");
        List<PatientCase> cases = summarizationService.getAllCases();
        return ResponseEntity.ok(cases);
    }

    @GetMapping("/{id}")
    public ResponseEntity<PatientCase> getCaseById(@PathVariable String id) {
        log.info("Fetching case: {}", id);
        PatientCase patientCase = summarizationService.getCaseById(id);
        return ResponseEntity.ok(patientCase);
    }

    @PutMapping("/{id}")
    public ResponseEntity<PatientCase> updateCase(
            @PathVariable String id,
            @RequestBody PatientCase patientCase) {
        log.info("Updating case: {}", id);
        PatientCase updated = summarizationService.updateCase(id, patientCase);
        return ResponseEntity.ok(updated);
    }

    @PostMapping("/{id}/summarize")
    public ResponseEntity<PatientCase> summarizeCase(@PathVariable String id) {
        log.info("Summarizing case: {}", id);
        PatientCase summarized = summarizationService.summarizeCase(id);
        return ResponseEntity.ok(summarized);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteCase(@PathVariable String id) {
        log.info("Deleting case: {}", id);
        summarizationService.deleteCase(id);
        return ResponseEntity.noContent().build();
    }

    @GetMapping("/health")
    public ResponseEntity<Map<String, String>> health() {
        return ResponseEntity.ok(Map.of("status", "UP"));
    }
}
