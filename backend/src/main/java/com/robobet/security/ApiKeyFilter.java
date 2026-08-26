package com.robobet.security;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;

@Component
public class ApiKeyFilter extends OncePerRequestFilter {
    private final String configured = System.getenv().getOrDefault("ROBO_API_KEY", "").trim();

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain chain)
            throws ServletException, IOException {
        if (configured.isEmpty() || "/api/health".equals(request.getRequestURI())) {
            chain.doFilter(request, response);
            return;
        }
        String supplied = request.getHeader("X-API-Key");
        if (!configured.equals(supplied)) {
            response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
            response.setContentType("application/json");
            response.getWriter().write("{\"detail\":\"AUTHENTICATION_REQUIRED\"}");
            return;
        }
        chain.doFilter(request, response);
    }
}
