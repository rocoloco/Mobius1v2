import React, { useState } from 'react';
import { Upload, Globe, FileText, ArrowRight, X, CheckCircle2 } from 'lucide-react';
import { PhysicalButton, RecessedScreen } from '../components/physical';

interface OnboardingProps {
  onComplete: (brandId: string) => void;
  onCancel?: () => void;
}

type OnboardingStep = 'input' | 'processing' | 'verify' | 'complete';

/**
 * The "Ingestion Bay" - Full-screen brand creation flow
 * Metaphor: "Fabrication Station" where Brand Cartridges are created
 */
export const Onboarding: React.FC<OnboardingProps> = ({
  onComplete,
  onCancel,
}) => {
  const [step, setStep] = useState<OnboardingStep>('input');
  const [websiteUrl, setWebsiteUrl] = useState('');
  const [pdfFile, setPdfFile] = useState<File | null>(null);
  const [logoFile, setLogoFile] = useState<File | null>(null);
  const [brandName, setBrandName] = useState('');

  const handleSubmit = async () => {
    if (!websiteUrl && !pdfFile) {
      return;
    }

    setStep('processing');

    // Simulate processing
    await new Promise((resolve) => setTimeout(resolve, 3000));

    setStep('verify');

    // Auto-set brand name from URL if not provided
    if (!brandName && websiteUrl) {
      try {
        const url = new URL(websiteUrl);
        setBrandName(url.hostname.replace('www.', '').split('.')[0]);
      } catch {
        // Invalid URL, ignore
      }
    }
  };

  const handleComplete = () => {
    setStep('complete');

    // Simulate completion
    setTimeout(() => {
      onComplete('new-brand-id');
    }, 1500);
  };

  return (
    <div className="h-screen w-full bg-background text-ink font-sans overflow-hidden flex flex-col items-center justify-center relative">
      {/* Close button */}
      {onCancel && (
        <button
          onClick={onCancel}
          className="absolute top-6 right-6 text-ink-muted hover:text-ink transition-colors"
        >
          <X size={24} />
        </button>
      )}

      {/* The Machine Housing */}
      <div className="w-full max-w-2xl bg-surface rounded-[2rem] shadow-soft p-8 relative">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-2xl font-black tracking-tight text-ink mb-2">
            INGESTION BAY
          </h1>
          <p className="text-sm text-ink-muted font-mono">
            Create a new Brand Cartridge
          </p>
        </div>

        {/* Progress Steps */}
        <div className="flex items-center justify-center gap-4 mb-8">
          <StepIndicator
            step={1}
            label="Input"
            active={step === 'input'}
            complete={step !== 'input'}
          />
          <div className="w-8 h-px bg-ink/20" />
          <StepIndicator
            step={2}
            label="Process"
            active={step === 'processing'}
            complete={step === 'verify' || step === 'complete'}
          />
          <div className="w-8 h-px bg-ink/20" />
          <StepIndicator
            step={3}
            label="Verify"
            active={step === 'verify'}
            complete={step === 'complete'}
          />
        </div>

        {/* Content */}
        <RecessedScreen className="p-6 min-h-[300px]">
          {step === 'input' && (
            <InputStep
              websiteUrl={websiteUrl}
              onWebsiteUrlChange={setWebsiteUrl}
              pdfFile={pdfFile}
              onPdfFileChange={setPdfFile}
              logoFile={logoFile}
              onLogoFileChange={setLogoFile}
            />
          )}

          {step === 'processing' && <ProcessingStep />}

          {step === 'verify' && (
            <VerifyStep
              brandName={brandName}
              onBrandNameChange={setBrandName}
              websiteUrl={websiteUrl}
            />
          )}

          {step === 'complete' && <CompleteStep />}
        </RecessedScreen>

        {/* Actions */}
        <div className="mt-6 flex justify-end gap-3">
          {step === 'input' && (
            <PhysicalButton
              variant="primary"
              onClick={handleSubmit}
              disabled={!websiteUrl && !pdfFile}
            >
              <span className="flex items-center gap-2">
                Process <ArrowRight size={14} />
              </span>
            </PhysicalButton>
          )}

          {step === 'verify' && (
            <>
              <PhysicalButton variant="ghost" onClick={() => setStep('input')}>
                Back
              </PhysicalButton>
              <PhysicalButton
                variant="primary"
                onClick={handleComplete}
                disabled={!brandName}
              >
                <span className="flex items-center gap-2">
                  Create Cartridge <ArrowRight size={14} />
                </span>
              </PhysicalButton>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

// --- Sub-components ---

interface StepIndicatorProps {
  step: number;
  label: string;
  active: boolean;
  complete: boolean;
}

const StepIndicator: React.FC<StepIndicatorProps> = ({
  step,
  label,
  active,
  complete,
}) => (
  <div className="flex flex-col items-center gap-1">
    <div
      className={`
        w-8 h-8 rounded-full flex items-center justify-center
        font-mono text-xs font-bold transition-all
        ${complete
          ? 'bg-success text-white'
          : active
            ? 'bg-accent text-white'
            : 'bg-ink/10 text-ink-muted'
        }
      `}
    >
      {complete ? <CheckCircle2 size={14} /> : step}
    </div>
    <span className="text-[10px] font-mono text-ink-muted uppercase">
      {label}
    </span>
  </div>
);

interface InputStepProps {
  websiteUrl: string;
  onWebsiteUrlChange: (url: string) => void;
  pdfFile: File | null;
  onPdfFileChange: (file: File | null) => void;
  logoFile: File | null;
  onLogoFileChange: (file: File | null) => void;
}

const InputStep: React.FC<InputStepProps> = ({
  websiteUrl,
  onWebsiteUrlChange,
  pdfFile,
  onPdfFileChange,
  logoFile,
  onLogoFileChange,
}) => (
  <div className="space-y-6">
    {/* Website URL */}
    <div>
      <label className="flex items-center gap-2 text-xs font-bold text-ink-muted uppercase tracking-wider mb-2">
        <Globe size={14} />
        Website URL
      </label>
      <input
        type="url"
        value={websiteUrl}
        onChange={(e) => onWebsiteUrlChange(e.target.value)}
        placeholder="https://stripe.com"
        className="w-full bg-surface shadow-pressed rounded-xl px-4 py-3 text-sm font-mono text-ink placeholder:text-ink-muted/50"
      />
      <p className="text-[10px] text-ink-muted mt-1 ml-1">
        AI will analyze the website's visual identity
      </p>
    </div>

    {/* PDF Upload */}
    <div>
      <label className="flex items-center gap-2 text-xs font-bold text-ink-muted uppercase tracking-wider mb-2">
        <FileText size={14} />
        Brand Guidelines PDF
      </label>
      <label className="block w-full bg-surface shadow-pressed rounded-xl p-6 text-center cursor-pointer hover:brightness-95 transition-all">
        <input
          type="file"
          accept=".pdf"
          onChange={(e) => onPdfFileChange(e.target.files?.[0] || null)}
          className="hidden"
        />
        <Upload size={24} className="mx-auto mb-2 text-ink-muted" />
        <span className="text-sm text-ink-muted">
          {pdfFile ? pdfFile.name : 'Click to upload PDF (max 50MB)'}
        </span>
      </label>
    </div>

    {/* Logo Upload */}
    <div>
      <label className="flex items-center gap-2 text-xs font-bold text-ink-muted uppercase tracking-wider mb-2">
        <Upload size={14} />
        Brand Logo (Optional)
      </label>
      <label className="block w-full bg-surface shadow-pressed rounded-xl p-4 text-center cursor-pointer hover:brightness-95 transition-all">
        <input
          type="file"
          accept=".svg,.png,.jpg,.jpeg"
          onChange={(e) => onLogoFileChange(e.target.files?.[0] || null)}
          className="hidden"
        />
        <span className="text-sm text-ink-muted">
          {logoFile ? logoFile.name : 'SVG preferred, or PNG with transparency'}
        </span>
      </label>
    </div>
  </div>
);

const ProcessingStep: React.FC = () => (
  <div className="flex flex-col items-center justify-center h-full py-12">
    <div className="w-16 h-16 rounded-full border-4 border-ink-muted/20 border-t-accent animate-spin mb-6" />
    <span className="font-mono text-sm text-ink-muted uppercase tracking-widest mb-2">
      Analyzing Brand Identity
    </span>
    <div className="flex gap-1">
      <div className="w-2 h-2 bg-accent rounded-full animate-pulse" />
      <div className="w-2 h-2 bg-accent rounded-full animate-pulse delay-75" />
      <div className="w-2 h-2 bg-accent rounded-full animate-pulse delay-150" />
    </div>
  </div>
);

interface VerifyStepProps {
  brandName: string;
  onBrandNameChange: (name: string) => void;
  websiteUrl: string;
}

const VerifyStep: React.FC<VerifyStepProps> = ({
  brandName,
  onBrandNameChange,
  websiteUrl,
}) => (
  <div className="space-y-6">
    <div className="text-center mb-4">
      <CheckCircle2 size={32} className="mx-auto text-success mb-2" />
      <p className="text-sm text-ink-muted">
        Brand identity extracted successfully
      </p>
    </div>

    {/* Brand Name */}
    <div>
      <label className="text-xs font-bold text-ink-muted uppercase tracking-wider mb-2 block">
        Brand Name
      </label>
      <input
        type="text"
        value={brandName}
        onChange={(e) => onBrandNameChange(e.target.value)}
        placeholder="Enter brand name"
        className="w-full bg-surface shadow-pressed rounded-xl px-4 py-3 text-sm font-mono text-ink placeholder:text-ink-muted/50"
      />
    </div>

    {/* Preview of extracted data (mock) */}
    <div className="bg-surface shadow-pressed rounded-xl p-4">
      <div className="text-[10px] font-bold text-ink-muted uppercase tracking-wider mb-3">
        Extracted Identity
      </div>
      <div className="grid grid-cols-2 gap-4 text-xs">
        <div>
          <span className="text-ink-muted">Archetype:</span>
          <span className="ml-2 font-bold text-ink">The Sage</span>
        </div>
        <div>
          <span className="text-ink-muted">Primary Color:</span>
          <span className="ml-2 font-bold text-ink">#635BFF</span>
        </div>
        <div>
          <span className="text-ink-muted">Voice:</span>
          <span className="ml-2 font-bold text-ink">Professional, Clear</span>
        </div>
        <div>
          <span className="text-ink-muted">Source:</span>
          <span className="ml-2 font-bold text-ink">{websiteUrl || 'PDF'}</span>
        </div>
      </div>
    </div>
  </div>
);

const CompleteStep: React.FC = () => (
  <div className="flex flex-col items-center justify-center h-full py-12">
    <div className="w-16 h-16 rounded-full bg-success/20 flex items-center justify-center mb-6">
      <CheckCircle2 size={32} className="text-success" />
    </div>
    <span className="font-mono text-sm text-ink uppercase tracking-widest mb-2">
      Cartridge Created
    </span>
    <p className="text-sm text-ink-muted">
      Ejecting to Workbench...
    </p>
  </div>
);

export default Onboarding;
