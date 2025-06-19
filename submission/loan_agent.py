from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import warnings

class DecisionType(Enum):
    APPROVED = "APPROVED"
    CONDITIONAL_APPROVAL = "CONDITIONAL_APPROVAL"
    DENIED = "DENIED"

class CreditScoreBand(Enum):
    POOR = "Poor"
    FAIR = "Fair"
    GOOD = "Good"
    VERY_GOOD = "Very Good"
    EXCELLENT = "Excellent"

@dataclass
class LoanDecision:
    applicant_name: str
    decision: DecisionType
    debt_to_income_ratio: float
    credit_score_band: CreditScoreBand
    explanation: str
    bias_flags: List[str]
    risk_factors: List[str]

class LoanApprovalAnalyzer:
    """
    Ethical AI-powered loan approval system implementing responsible lending practices
    with comprehensive bias detection and regulatory compliance features.
    """
    
    # Industry-standard thresholds
    DTI_THRESHOLD = 0.30  # 30% debt-to-income ratio
    MIN_CREDIT_SCORE = 650
    
    # FICO Score ranges
    CREDIT_SCORE_BANDS = {
        (0, 579): CreditScoreBand.POOR,
        (580, 669): CreditScoreBand.FAIR,
        (670, 739): CreditScoreBand.GOOD,
        (740, 799): CreditScoreBand.VERY_GOOD,
        (800, 850): CreditScoreBand.EXCELLENT
    }
    
    def __init__(self):
        """Initialize the loan approval analyzer with ethical AI principles."""
        self.decisions_log: List[LoanDecision] = []
        
    def calculate_debt_to_income_ratio(self, income: float, debt: float) -> float:
        """
        Calculate debt-to-income ratio with input validation.
        
        Args:
            income: Annual gross income
            debt: Total monthly debt payments (annualized)
            
        Returns:
            Debt-to-income ratio as decimal (e.g., 0.25 for 25%)
            
        Raises:
            ValueError: If income is zero or negative, or debt is negative
        """
        if income <= 0:
            raise ValueError("Income must be positive")
        if debt < 0:
            raise ValueError("Debt cannot be negative")
            
        return debt / income
    
    def get_credit_score_band(self, credit_score: int) -> CreditScoreBand:
        """
        Categorize credit score using industry-standard FICO ranges.
        
        Args:
            credit_score: FICO credit score (300-850)
            
        Returns:
            CreditScoreBand enum representing score quality
            
        Raises:
            ValueError: If credit score is outside valid range
        """
        if not 300 <= credit_score <= 850:
            raise ValueError("Credit score must be between 300 and 850")
            
        for (min_score, max_score), band in self.CREDIT_SCORE_BANDS.items():
            if min_score <= credit_score <= max_score:
                return band
        
        raise ValueError("Credit score categorization failed")
    
    def detect_potential_bias(self, applicant: Dict, decision: DecisionType) -> List[str]:
        """
        Identify potential discriminatory patterns in loan decisions.
        
        Args:
            applicant: Dictionary containing applicant information
            decision: Loan decision made by the system
            
        Returns:
            List of bias warning flags
        """
        bias_flags = []
        
        # Age discrimination detection
        age = applicant.get('age', 0)
        if age < 35 and decision == DecisionType.DENIED:
            bias_flags.append("AGE_BIAS_RISK: Young applicant denial - verify decision not age-based")
        
        # Income-based bias detection
        income = applicant.get('income', 0)
        if income < 50000 and decision == DecisionType.DENIED:
            bias_flags.append("INCOME_BIAS_RISK: Lower-income denial - ensure decision based on DTI, not absolute income")
        
        # Credit score bias - recognizing limitations
        credit_score = applicant.get('credit_score', 0)
        if 580 <= credit_score < 650:
            bias_flags.append("CREDIT_SCORE_LIMITATION: Fair credit score ≠ inability to repay - consider full financial picture")
        
        # Historical lending bias patterns
        if decision == DecisionType.DENIED and len([f for f in bias_flags if 'BIAS_RISK' in f]) >= 2:
            bias_flags.append("MULTIPLE_BIAS_INDICATORS: Decision requires human oversight for fairness review")
        
        return bias_flags
    
    def assess_risk_factors(self, applicant: Dict, dti_ratio: float, credit_band: CreditScoreBand) -> List[str]:
        """
        Identify specific risk factors for transparent decision-making.
        
        Args:
            applicant: Applicant information dictionary
            dti_ratio: Calculated debt-to-income ratio
            credit_band: Credit score quality band
            
        Returns:
            List of identified risk factors
        """
        risk_factors = []
        
        if dti_ratio > self.DTI_THRESHOLD:
            risk_factors.append(f"High debt-to-income ratio: {dti_ratio:.1%} exceeds {self.DTI_THRESHOLD:.0%} threshold")
        
        if applicant['credit_score'] < self.MIN_CREDIT_SCORE:
            risk_factors.append(f"Credit score {applicant['credit_score']} below minimum {self.MIN_CREDIT_SCORE}")
        
        if credit_band == CreditScoreBand.POOR:
            risk_factors.append("Poor credit history indicates elevated default risk")
        
        if dti_ratio > 0.40:
            risk_factors.append("Extremely high debt burden may impact repayment capacity")
        
        return risk_factors
    
    def make_loan_decision(self, applicant: Dict) -> DecisionType:
        """
        Generate loan approval decision using established financial criteria.
        
        Args:
            applicant: Dictionary with keys: name, income, credit_score, debt, age
            
        Returns:
            DecisionType enum representing approval decision
        """
        dti_ratio = self.calculate_debt_to_income_ratio(applicant['income'], applicant['debt'])
        credit_score = applicant['credit_score']
        credit_band = self.get_credit_score_band(credit_score)
        
        # Primary approval criteria: DTI < 30% AND credit score >= 650
        meets_dti_threshold = dti_ratio < self.DTI_THRESHOLD
        meets_credit_threshold = credit_score >= self.MIN_CREDIT_SCORE
        
        if meets_dti_threshold and meets_credit_threshold:
            return DecisionType.APPROVED
        elif meets_credit_threshold and dti_ratio < 0.35:
            # Good credit with slightly elevated DTI
            return DecisionType.CONDITIONAL_APPROVAL
        elif meets_dti_threshold and credit_score >= 620:
            # Good DTI with fair credit
            return DecisionType.CONDITIONAL_APPROVAL
        else:
            return DecisionType.DENIED
    
    def generate_decision_explanation(self, applicant: Dict, decision: DecisionType, 
                                    dti_ratio: float, credit_band: CreditScoreBand, 
                                    risk_factors: List[str]) -> str:
        """
        Create transparent explanation for loan decision.
        
        Args:
            applicant: Applicant information
            decision: Loan decision made
            dti_ratio: Debt-to-income ratio
            credit_band: Credit score quality band
            risk_factors: Identified risk factors
            
        Returns:
            Human-readable explanation of decision rationale
        """
        base_info = (f"DTI: {dti_ratio:.1%}, Credit Score: {applicant['credit_score']} ({credit_band.value})")
        
        if decision == DecisionType.APPROVED:
            return f"APPROVED - {base_info}. Meets all standard lending criteria."
        elif decision == DecisionType.CONDITIONAL_APPROVAL:
            return f"CONDITIONAL APPROVAL - {base_info}. Requires additional verification or terms adjustment."
        else:
            risk_summary = "; ".join(risk_factors) if risk_factors else "Multiple risk factors identified"
            return f"DENIED - {base_info}. Risk factors: {risk_summary}"
    
    def evaluate_applicant(self, applicant: Dict) -> LoanDecision:
        """
        Comprehensive applicant evaluation with bias detection and transparency.
        
        Args:
            applicant: Dictionary containing applicant financial information
            
        Returns:
            LoanDecision object with complete analysis results
        """
        try:
            # Calculate financial metrics
            dti_ratio = self.calculate_debt_to_income_ratio(applicant['income'], applicant['debt'])
            credit_band = self.get_credit_score_band(applicant['credit_score'])
            
            # Make decision
            decision = self.make_loan_decision(applicant)
            
            # Assess risks and bias
            risk_factors = self.assess_risk_factors(applicant, dti_ratio, credit_band)
            bias_flags = self.detect_potential_bias(applicant, decision)
            
            # Generate explanation
            explanation = self.generate_decision_explanation(
                applicant, decision, dti_ratio, credit_band, risk_factors
            )
            
            # Create decision record
            loan_decision = LoanDecision(
                applicant_name=applicant['name'],
                decision=decision,
                debt_to_income_ratio=dti_ratio,
                credit_score_band=credit_band,
                explanation=explanation,
                bias_flags=bias_flags,
                risk_factors=risk_factors
            )
            
            self.decisions_log.append(loan_decision)
            return loan_decision
            
        except Exception as e:
            raise ValueError(f"Error evaluating applicant {applicant.get('name', 'Unknown')}: {str(e)}")
    
    def process_applicant_batch(self, applicants: List[Dict]) -> List[LoanDecision]:
        """
        Process multiple loan applications with comprehensive analysis.
        
        Args:
            applicants: List of applicant dictionaries
            
        Returns:
            List of LoanDecision objects for all applicants
        """
        decisions = []
        for applicant in applicants:
            decision = self.evaluate_applicant(applicant)
            decisions.append(decision)
        return decisions
    
    def generate_audit_report(self) -> str:
        """
        Generate regulatory compliance audit trail.
        
        Returns:
            Formatted audit report string
        """
        if not self.decisions_log:
            return "No decisions recorded for audit."
        
        report = "=== LOAN APPROVAL AUDIT REPORT ===\n\n"
        
        # Decision summary
        decision_counts = {}
        for decision in self.decisions_log:
            decision_type = decision.decision.value
            decision_counts[decision_type] = decision_counts.get(decision_type, 0) + 1
        
        report += "Decision Summary:\n"
        for decision_type, count in decision_counts.items():
            report += f"  {decision_type}: {count}\n"
        
        # Bias flag summary
        all_bias_flags = []
        for decision in self.decisions_log:
            all_bias_flags.extend(decision.bias_flags)
        
        if all_bias_flags:
            report += f"\nBias Flags Raised: {len(all_bias_flags)}\n"
            unique_flags = set(all_bias_flags)
            for flag in unique_flags:
                count = all_bias_flags.count(flag)
                report += f"  {flag}: {count} instances\n"
        
        return report

# Dataset and execution
applicants = [
    {"name": "Alice", "income": 62000, "credit_score": 710, "debt": 22000, "age": 33},
    {"name": "Bob", "income": 45000, "credit_score": 640, "debt": 18000, "age": 41},
    {"name": "Carol", "income": 38000, "credit_score": 580, "debt": 25000, "age": 29}
]

def main():
    """Execute loan approval analysis with comprehensive reporting."""
    analyzer = LoanApprovalAnalyzer()
    
    print("=== ETHICAL AI LOAN APPROVAL SYSTEM ===\n")
    
    # Process all applicants
    decisions = analyzer.process_applicant_batch(applicants)
    
    # Display individual results
    for decision in decisions:
        print(f"Applicant: {decision.applicant_name}")
        print(f"Decision: {decision.decision.value}")
        print(f"Explanation: {decision.explanation}")
        
        if decision.bias_flags:
            print("Bias Flags:")
            for flag in decision.bias_flags:
                print(f"  ⚠️  {flag}")
        
        if decision.risk_factors:
            print("Risk Factors:")
            for factor in decision.risk_factors:
                print(f"  📊 {factor}")
        
        print("-" * 60)
    
    # Generate audit report
    print("\n" + analyzer.generate_audit_report())

if __name__ == "__main__":
    main()
