"""
Professional scanning engine for QAInspect Pro
Multi-threaded security and performance analysis for websites
"""

import asyncio
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import ssl
import socket
from datetime import datetime
import httpx
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from html.parser import HTMLParser

logger = logging.getLogger(__name__)


class SeverityLevel(str, Enum):
    """Security finding severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class SecurityFinding:
    """Individual security finding"""
    title: str
    description: str
    severity: SeverityLevel
    remediation: str
    evidence: Dict[str, Any]
    cwe_id: Optional[str] = None
    cvss_score: Optional[float] = None


@dataclass
class PerformanceMetric:
    """Performance measurement"""
    metric_name: str
    value: float
    unit: str
    threshold: float
    status: str  # pass, warning, fail


@dataclass
class ScanResult:
    """Complete scan result"""
    url: str
    scan_time: float
    security_score: float
    performance_score: float
    security_findings: List[Dict]
    performance_metrics: List[Dict]
    recommendations: List[str]
    timestamp: str
    seo_score: float = 100.0
    seo_findings: List[Dict] = None


class SecurityAuditor:
    """Security analysis component"""
    
    # Security headers that should be present
    REQUIRED_HEADERS = {
        "Strict-Transport-Security": {
            "description": "Enforces HTTPS connections",
            "remediation": "Add 'Strict-Transport-Security: max-age=31536000; includeSubDomains' header"
        },
        "Content-Security-Policy": {
            "description": "Prevents XSS attacks",
            "remediation": "Implement CSP with strict directives"
        },
        "X-Content-Type-Options": {
            "description": "Prevents MIME sniffing",
            "remediation": "Add 'X-Content-Type-Options: nosniff' header"
        },
        "X-Frame-Options": {
            "description": "Prevents clickjacking",
            "remediation": "Add 'X-Frame-Options: DENY' or 'SAMEORIGIN' header"
        },
        "X-XSS-Protection": {
            "description": "Browser XSS protection",
            "remediation": "Add 'X-XSS-Protection: 1; mode=block' header"
        },
        "Referrer-Policy": {
            "description": "Controls referrer information",
            "remediation": "Add 'Referrer-Policy: no-referrer' header"
        }
    }
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.findings: List[SecurityFinding] = []
    
    async def audit_ssl_tls(self, url: str) -> Tuple[bool, Optional[str], Dict[str, Any]]:
        """
        Audit SSL/TLS certificate configuration
        
        Returns:
            Tuple of (is_valid, error_message, certificate_info)
        """
        try:
            hostname = url.replace("https://", "").replace("http://", "").split("/")[0]
            
            # Create SSL context
            context = ssl.create_default_context()
            
            with socket.create_connection((hostname, 443), timeout=self.timeout) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    cert_der = ssock.getpeercert(binary_form=True)
                    
                    cert_info = {
                        "subject": dict(x[0] for x in cert.get("subject", [])),
                        "issuer": dict(x[0] for x in cert.get("issuer", [])),
                        "version": cert.get("version"),
                        "not_before": cert.get("notBefore"),
                        "not_after": cert.get("notAfter"),
                        "san": cert.get("subjectAltName", [])
                    }
                    
                    return True, None, cert_info
        
        except ssl.SSLError as e:
            return False, f"SSL Error: {str(e)}", {}
        except socket.timeout:
            return False, "Connection timeout", {}
        except Exception as e:
            return False, f"Certificate audit failed: {str(e)}", {}
    
    async def audit_headers(self, headers: Dict[str, str]) -> Tuple[List[SecurityFinding], float]:
        """
        Audit response headers for security best practices
        
        Returns:
            Tuple of (findings_list, security_score_contribution)
        """
        findings = []
        score = 100.0
        headers_lower = {k.lower(): v for k, v in headers.items()}
        
        # Check for required headers
        for header_name, header_info in self.REQUIRED_HEADERS.items():
            header_key = header_name.lower()
            
            if header_key not in headers_lower:
                findings.append(SecurityFinding(
                    title=f"Missing {header_name} Header",
                    description=header_info["description"],
                    severity=SeverityLevel.HIGH if header_name in [
                        "Strict-Transport-Security",
                        "X-Frame-Options"
                    ] else SeverityLevel.MEDIUM,
                    remediation=header_info["remediation"],
                    evidence={"missing_header": header_name},
                    cwe_id="693"  # Protection Mechanism Failure
                ))
                score -= 10 if header_name in ["Strict-Transport-Security", "X-Frame-Options"] else 5
        
        # Check for information disclosure headers
        disclosure_headers = ["Server", "X-Powered-By", "X-AspNet-Version"]
        for header in disclosure_headers:
            if header in headers:
                findings.append(SecurityFinding(
                    title=f"Information Disclosure: {header} Header",
                    description="Server version information is exposed",
                    severity=SeverityLevel.LOW,
                    remediation=f"Remove the {header} header to avoid exposing server information",
                    evidence={"exposed_header": header, "value": headers[header]},
                    cwe_id="200"  # Exposure of Sensitive Information
                ))
                score -= 5
        
        return findings, max(score, 0)
    
    async def audit_url(self, url: str) -> Dict[str, Any]:
        """Execute full security audit on URL"""
        audit_results = {
            "url": url,
            "findings": [],
            "score": 100.0,
            "ssl_valid": False,
            "certificate_info": None,
            "headers": {}
        }
        
        try:
            # Audit SSL/TLS
            ssl_valid, ssl_error, cert_info = await self.audit_ssl_tls(url)
            audit_results["ssl_valid"] = ssl_valid
            audit_results["certificate_info"] = cert_info
            
            if not ssl_valid:
                audit_results["findings"].append({
                    "title": "SSL/TLS Configuration Issue",
                    "description": ssl_error,
                    "severity": SeverityLevel.CRITICAL.value,
                    "remediation": "Fix SSL/TLS configuration",
                    "evidence": {"error": ssl_error}
                })
                audit_results["score"] -= 30
            
            # Get headers
            async with httpx.AsyncClient(verify=False, timeout=self.timeout) as client:
                try:
                    response = await client.head(url, follow_redirects=True)
                    headers = dict(response.headers)
                    audit_results["headers"] = headers
                    
                    # Audit headers
                    header_findings, header_score = await self.audit_headers(headers)
                    audit_results["findings"].extend([asdict(f) for f in header_findings])
                    audit_results["score"] = header_score
                    
                except Exception as e:
                    audit_results["findings"].append({
                        "title": "Failed to retrieve headers",
                        "description": str(e),
                        "severity": SeverityLevel.INFO.value,
                        "remediation": "Check URL accessibility"
                    })
        
        except Exception as e:
            logger.error(f"Security audit failed for {url}: {str(e)}")
            audit_results["findings"].append({
                "title": "Audit Error",
                "description": str(e),
                "severity": SeverityLevel.INFO.value
            })
        
        return audit_results


class PerformanceAnalyzer:
    """Performance analysis component"""
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.metrics: List[PerformanceMetric] = []
    
    async def measure_response_time(self, url: str) -> Dict[str, Any]:
        """
        Measure response time and TTLB (Time To Last Byte)
        
        Returns:
            Dict with timing metrics
        """
        metrics = {
            "dns_time": 0,
            "connect_time": 0,
            "ttfb": 0,  # Time to First Byte
            "ttlb": 0,  # Time to Last Byte
            "status_code": 0,
            "content_length": 0,
            "score": 0
        }
        
        try:
            async with httpx.AsyncClient(verify=False, timeout=self.timeout) as client:
                start_time = time.time()
                response = await client.get(url, follow_redirects=True)
                end_time = time.time()
                
                total_time = (end_time - start_time) * 1000  # Convert to ms
                
                metrics["ttlb"] = round(total_time, 2)
                metrics["status_code"] = response.status_code
                metrics["content_length"] = len(response.content)
                
                # Calculate performance score (target < 1000ms)
                if total_time < 1000:
                    metrics["score"] = min(100, 100 - (total_time / 10))
                else:
                    metrics["score"] = max(0, 100 - (total_time / 10))
        
        except asyncio.TimeoutError:
            metrics["status_code"] = 504
        except Exception as e:
            logger.error(f"Performance measurement failed: {str(e)}")
        
        return metrics
    
    async def analyze_payload(self, url: str) -> Dict[str, Any]:
        """Analyze response payload size and efficiency"""
        analysis = {
            "total_size_kb": 0,
            "score": 0,
            "recommendations": []
        }
        
        try:
            async with httpx.AsyncClient(verify=False, timeout=self.timeout) as client:
                response = await client.get(url, follow_redirects=True)
                size_kb = len(response.content) / 1024
                analysis["total_size_kb"] = round(size_kb, 2)
                
                # Scoring: 0-100 KB = 100, 100+ KB = decreasing
                if size_kb <= 100:
                    analysis["score"] = 100
                else:
                    analysis["score"] = max(0, 100 - ((size_kb - 100) / 10))
                
                # Recommendations
                if size_kb > 500:
                    analysis["recommendations"].append(
                        "Consider implementing gzip compression to reduce payload size"
                    )
                if size_kb > 1000:
                    analysis["recommendations"].append(
                        "Payload is over 1MB. Optimize images and remove unnecessary content"
                    )
        
        except Exception as e:
            logger.error(f"Payload analysis failed: {str(e)}")
        
        return analysis
    
    async def analyze_url(self, url: str) -> Dict[str, Any]:
        """Execute full performance analysis"""
        return {
            "response_time": await self.measure_response_time(url),
            "payload": await self.analyze_payload(url)
        }


class SEOAndAccessibilityHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = None
        self.meta_description = None
        self.has_h1 = False
        self.images = []
        self.links = []
        self.semantic_elements = set()
        
        self.in_title = False
        self.current_tag = None
        
    def handle_starttag(self, tag, attrs):
        self.current_tag = tag
        attrs_dict = dict(attrs)
        
        if tag == "title":
            self.in_title = True
        elif tag == "meta":
            if attrs_dict.get("name") == "description":
                self.meta_description = attrs_dict.get("content")
        elif tag == "h1":
            self.has_h1 = True
        elif tag == "img":
            self.images.append({
                "src": attrs_dict.get("src", ""),
                "alt": attrs_dict.get("alt")
            })
        elif tag == "a":
            self.links.append({
                "href": attrs_dict.get("href", ""),
                "text": ""
            })
        elif tag in {"header", "nav", "main", "footer", "article", "section", "aside"}:
            self.semantic_elements.add(tag)

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        self.current_tag = None

    def handle_data(self, data):
        if self.in_title:
            self.title = (self.title or "") + data
        elif self.current_tag == "a" and self.links:
            self.links[-1]["text"] = (self.links[-1]["text"] or "") + data


class SEOAndAccessibilityAuditor:
    """SEO & Accessibility SQA analysis component"""
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        
    async def audit_url(self, url: str) -> Dict[str, Any]:
        """Perform SEO and Accessibility SQA audit"""
        findings = []
        score = 100.0
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, follow_redirects=True)
                
                parser = SEOAndAccessibilityHTMLParser()
                parser.feed(response.text)
                
                # 1. Title Audit
                if not parser.title:
                    score -= 15
                    findings.append({
                        "title": "Missing Page Title",
                        "description": "The page does not have a <title> element, which is critical for search engine indexing and browser tab labeling.",
                        "severity": "high",
                        "remediation": "Add a descriptive <title> tag inside the <head> block."
                    })
                elif len(parser.title.strip()) < 10 or len(parser.title.strip()) > 60:
                    score -= 5
                    findings.append({
                        "title": "Suboptimal Title Length",
                        "description": f"Page title '{parser.title.strip()}' has a length of {len(parser.title.strip())} characters. Optimal length is between 10 and 60 characters.",
                        "severity": "low",
                        "remediation": "Adjust title length to be descriptive and concise (10-60 characters)."
                    })
                    
                # 2. Meta Description Audit
                if not parser.meta_description:
                    score -= 15
                    findings.append({
                        "title": "Missing Meta Description",
                        "description": "The page does not have a meta description, which is displayed in search results to summarize page contents.",
                        "severity": "high",
                        "remediation": "Add <meta name='description' content='...'> in the <head> section."
                    })
                elif len(parser.meta_description.strip()) < 50 or len(parser.meta_description.strip()) > 160:
                    score -= 5
                    findings.append({
                        "title": "Suboptimal Meta Description Length",
                        "description": f"Meta description is {len(parser.meta_description.strip())} characters. Optimal length is between 50 and 160 characters.",
                        "severity": "low",
                        "remediation": "Adjust meta description to fit optimally within search engine snippets (50-160 characters)."
                    })
                    
                # 3. Heading 1 Audit
                if not parser.has_h1:
                    score -= 15
                    findings.append({
                        "title": "Missing H1 Header Tag",
                        "description": "No <h1> element found on the page. H1 headings define the primary page topic and are critical for a11y screen readers and search engine crawlers.",
                        "severity": "medium",
                        "remediation": "Organize your content structure to include exactly one primary <h1> tag."
                    })
                    
                # 4. Images Alt Attributes Audit
                total_imgs = len(parser.images)
                missing_alt = sum(1 for img in parser.images if img["alt"] is None or img["alt"].strip() == "")
                if total_imgs > 0 and missing_alt > 0:
                    alt_score_penalty = min(20, int((missing_alt / total_imgs) * 20))
                    score -= alt_score_penalty
                    findings.append({
                        "title": f"Images Missing Alt Text ({missing_alt}/{total_imgs})",
                        "description": f"{missing_alt} out of {total_imgs} images do not have an 'alt' attribute, which is essential for visually impaired users utilizing screen readers.",
                        "severity": "medium",
                        "remediation": "Ensure all <img> tags have a descriptive 'alt' attribute explaining the image context."
                    })
                    
                # 5. Semantic Elements Audit
                missing_semantics = {"header", "nav", "main", "footer"} - parser.semantic_elements
                if len(missing_semantics) > 0:
                    score -= len(missing_semantics) * 5
                    findings.append({
                        "title": f"Lacks Semantic HTML5 Elements",
                        "description": f"Missing tags: {', '.join(missing_semantics)}. Semantic markup makes it easier for search engine bots and assist-technologies to parse the structure.",
                        "severity": "low",
                        "remediation": "Use HTML5 semantic elements (<header>, <nav>, <main>, <footer>) instead of generic <div> blocks."
                    })
                    
        except Exception as e:
            logger.error(f"SEO & Accessibility audit failed: {str(e)}")
            score = 0.0
            findings.append({
                "title": "Audit Pipeline Failed",
                "description": f"Encountered connection or parse exception: {str(e)}",
                "severity": "high",
                "remediation": "Verify host availability and content type format."
            })
            
        return {
            "score": max(0.0, score),
            "findings": findings
        }


class URLScanner:
    """Main URL scanner - orchestrates security and performance analysis"""
    
    def __init__(self, max_workers: int = 5, timeout: int = 10):
        self.max_workers = max_workers
        self.timeout = timeout
        self.security_auditor = SecurityAuditor(timeout=timeout)
        self.performance_analyzer = PerformanceAnalyzer(timeout=timeout)
        self.seo_auditor = SEOAndAccessibilityAuditor(timeout=timeout)
    
    async def scan_url(self, url: str) -> ScanResult:
        """
        Perform comprehensive scan on URL
        
        Args:
            url: Target URL to scan
            
        Returns:
            ScanResult object with all findings
        """
        start_time = time.time()
        logger.info(f"Starting scan for {url}")
        
        # Validate URL format
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"
        
        # Run scans in parallel
        security_task = asyncio.create_task(
            self.security_auditor.audit_url(url)
        )
        performance_task = asyncio.create_task(
            self.performance_analyzer.analyze_url(url)
        )
        seo_task = asyncio.create_task(
            self.seo_auditor.audit_url(url)
        )
        
        security_result = await security_task
        performance_result = await performance_task
        seo_result = await seo_task
        
        # Generate recommendations based on findings
        recommendations = self._generate_recommendations(security_result, performance_result, seo_result)
        
        scan_time = time.time() - start_time
        
        return ScanResult(
            url=url,
            scan_time=round(scan_time, 2),
            security_score=round(security_result.get("score", 0), 1),
            performance_score=round(performance_result["response_time"].get("score", 0), 1),
            security_findings=security_result.get("findings", []),
            performance_metrics=[
                {"metric": k, "value": v} 
                for k, v in performance_result["response_time"].items()
            ] + [
                {"metric": "payload_size_kb", "value": performance_result["payload"]["total_size_kb"]},
                {"metric": "payload_score", "value": performance_result["payload"]["score"]}
            ],
            recommendations=recommendations,
            timestamp=datetime.utcnow().isoformat(),
            seo_score=round(seo_result.get("score", 0), 1),
            seo_findings=seo_result.get("findings", [])
        )
    
    def _generate_recommendations(
        self,
        security_result: Dict,
        performance_result: Dict,
        seo_result: Dict = None
    ) -> List[str]:
        """Generate AI-style recommendations based on scan results"""
        recommendations = []
        
        # Security recommendations
        critical_findings = [f for f in security_result.get("findings", [])
                           if f.get("severity") == "critical"]
        
        if critical_findings:
            recommendations.append(
                f"🔴 Critical: {len(critical_findings)} critical security issues found. "
                "Address these immediately."
            )
        
        if not security_result.get("ssl_valid"):
            recommendations.append(
                "🔒 Ensure SSL/TLS is properly configured and certificate is valid"
            )
        
        # Performance recommendations
        ttlb = performance_result["response_time"].get("ttlb", 0)
        if ttlb > 5000:
            recommendations.append(
                "⚡ Performance: Response time is very slow (>5s). "
                "Consider caching, CDN, or backend optimization."
            )
        elif ttlb > 2000:
            recommendations.append(
                "⚡ Performance: Response time is above 2 seconds. "
                "Implement caching strategies and optimize assets."
            )
        
        # Payload recommendations
        recommendations.extend(
            performance_result["payload"].get("recommendations", [])
        )
        
        # SEO & Accessibility recommendations
        if seo_result:
            seo_findings = seo_result.get("findings", [])
            for f in seo_findings:
                if f.get("severity") in ("critical", "high", "medium"):
                    recommendations.append(
                        f"🔍 SQA a11y/SEO: {f.get('title')}. {f.get('remediation')}"
                    )
        
        return recommendations
    
    async def scan_multiple_urls(self, urls: List[str]) -> List[ScanResult]:
        """Scan multiple URLs concurrently"""
        tasks = [self.scan_url(url) for url in urls]
        return await asyncio.gather(*tasks)


# Convenience function for FastAPI integration
async def scan_single_url(url: str) -> Dict[str, Any]:
    """Scan a single URL and return results as dict"""
    scanner = URLScanner()
    result = await scanner.scan_url(url)
    return asdict(result)


async def analyze_target(url: str) -> Dict[str, Any]:
    """
    Orchestrate security and performance analysis and format output 
    specifically for the dashboard and test cases engine.
    """
    scanner = URLScanner()
    result = await scanner.scan_url(url)
    
    # Extract load time from performance metrics
    load_time_ms = 0.0
    for m in result.performance_metrics:
        if m.get("metric") == "ttlb":
            load_time_ms = m.get("value", 0.0)
            break
    load_time_seconds = load_time_ms / 1000.0

    # Determine security status and performance status
    perf_status = "Passed" if load_time_seconds <= 2.0 else "Failed"
    
    # Extract security issues from security findings titles
    issues = []
    for f in result.security_findings:
        issues.append(f.get("title", "Security Finding"))
    
    sec_status = "Passed" if len(issues) == 0 else "Failed"
    
    # Extract SEO/a11y issues from findings safely
    seo_issues = []
    for f in (result.seo_findings or []):
        seo_issues.append(f.get("title", "SEO Issue"))
    
    seo_status = "Passed" if len(seo_issues) == 0 else "Failed"
    
    return {
        "performance": {
            "status": perf_status,
            "load_time_seconds": load_time_seconds,
            "error": None
        },
        "security": {
            "status": sec_status,
            "issues": issues,
            "error": None
        },
        "seo": {
            "status": seo_status,
            "issues": seo_issues,
            "error": None
        }
    }

