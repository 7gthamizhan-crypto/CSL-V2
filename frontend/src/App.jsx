import React, { useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Header } from './components/Header';
import { Sidebar } from './components/Sidebar';
import { Dashboard } from './pages/Dashboard';
import { AIRecommendationCenter } from './pages/AIRecommendationCenter';
import { RiskAssessment } from './pages/RiskAssessment';
import { FraudAnomalyDetection } from './pages/FraudAnomalyDetection';
import { DocumentIntelligence } from './pages/DocumentIntelligence';
import { HSCodeIntelligence } from './pages/HSCodeIntelligence';
import { ReadinessValidation } from './pages/ReadinessValidation';
import { DailySchedule } from './pages/DailySchedule';
import { ContainerQueue } from './pages/ContainerQueue';
import { Resources } from './pages/Resources';
import { ExaminationOutcome } from './pages/ExaminationOutcome';
import { Simulator } from './pages/Simulator';
import { DataQualityAIReadiness } from './pages/DataQualityAIReadiness';
import { AIGovernanceAudit } from './pages/AIGovernanceAudit';
import { Reports } from './pages/Reports';
import { Settings } from './pages/Settings';

export function App() {
  const [mobileOpen, setMobileOpen] = useState(false);

  const toggleMobileSidebar = () => {
    setMobileOpen(prev => !prev);
  };

  const closeMobileSidebar = () => {
    setMobileOpen(false);
  };

  return (
    <BrowserRouter>
      <div className="app-container">
        <Sidebar mobileOpen={mobileOpen} closeMobileSidebar={closeMobileSidebar} />
        <div className="main-wrapper">
          <Header toggleMobileSidebar={toggleMobileSidebar} />
          <main className="content-area">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/recommendations" element={<AIRecommendationCenter />} />
              <Route path="/risk" element={<RiskAssessment />} />
              <Route path="/anomalies" element={<FraudAnomalyDetection />} />
              <Route path="/documents" element={<DocumentIntelligence />} />
              <Route path="/hs-intelligence" element={<HSCodeIntelligence />} />
              <Route path="/readiness" element={<ReadinessValidation />} />
              <Route path="/schedule" element={<DailySchedule />} />
              <Route path="/containers" element={<ContainerQueue />} />
              <Route path="/resources" element={<Resources />} />
              <Route path="/outcomes" element={<ExaminationOutcome />} />
              <Route path="/simulator" element={<Simulator />} />
              <Route path="/data-quality" element={<DataQualityAIReadiness />} />
              <Route path="/audit" element={<AIGovernanceAudit />} />
              <Route path="/reports" element={<Reports />} />
              <Route path="/settings" element={<Settings />} />
            </Routes>
          </main>
        </div>
      </div>
    </BrowserRouter>
  );
}

export default App;
