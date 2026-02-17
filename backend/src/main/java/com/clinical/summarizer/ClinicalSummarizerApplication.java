package com.clinical.summarizer;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.web.reactive.function.client.WebClient;

@SpringBootApplication
public class ClinicalSummarizerApplication {

    public static void main(String[] args) {
        SpringApplication.run(ClinicalSummarizerApplication.class, args);
    }

    @Bean
    public WebClient webClient() {
        return WebClient.builder().build();
    }
}
