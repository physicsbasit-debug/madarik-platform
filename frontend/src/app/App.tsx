import { ArrowLeft, ArrowRight, DatabaseZap } from "lucide-react";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { WorkflowStatusStrip } from "../components/WorkflowStatusStrip";
import { WorkspaceShell } from "../components/WorkspaceShell";
import { WorkspaceSidebar } from "../components/WorkspaceSidebar";
import { WorkspaceTopBar } from "../components/WorkspaceTopBar";
import {
  getLegacyStepForStage,
  getWorkflowStageIndex,
  steps,
  type WorkflowStageKey,
} from "../constants/steps";
import {
  defaultMetadata,
  sampleGlossary,
  sampleQuestions,
} from "../data/mockProject";
import { AuthPanel } from "../features/auth/AuthPanel";
import { ExportStep } from "../features/export/ExportStep";
import { StartWorkspace } from "../features/workflow/StartWorkspace";
import { UnifiedReviewWorkspace } from "../features/workflow/UnifiedReviewWorkspace";
import {
  bootstrapOwner,
  clearAnswerKey,
  clearEducationalAnalysis,
  clearQualityTools,
  bulkUpdateQuestionStatus,
  createAuthAccount,
  createProject,
  cropQuestionLayoutAsset,
  exportProjectDocx,
  exportProjectPdf,
  exportProjectSnapshot,
  generateGlossaryFromQuestions,
  deleteProject,
  deletePdfLayoutAsset,
  deleteQuestionAsset,
  linkQuestionLayoutAsset,
  unlinkQuestionLayoutAsset,
  deleteSchoolLogo,
  loadDemoContent,
  parseExtractedQuestions,
  reorderQuestions,
  setUploadedFileInfo,
  translateProjectQuestions,
  retryQuestionTranslation,
  uploadQuestionAsset,
  uploadPdfAndExtractText,
  uploadPdfOcrAndExtractText,
  uploadImageAndExtractText,
  uploadSchoolLogo,
  updateGlossaryTerm as updateGlossaryTermOnServer,
  updateProjectMetadata,
  updateProjectStep,
  updateQuestion as updateQuestionOnServer,
  getTranslationProviderStatus,
  runFullExamEndToEndAcceptance,
  generateAnswerKeyDraft,
  generateEducationalAnalysis,
  generateQualityTools,
  getAuthStatus,
  getCurrentAccount,
  getProject,
  getProjectReadiness,
  importProjectSnapshot,
  listAuthAccounts,
  login,
  logout,
  listProjects,
  updateAuthAccount,
} from "../services/api";
import ScienceTaskHome from "../features/workflow/ScienceTaskHome";
import QuickTranslationWorkspace from "../features/workflow/QuickTranslationWorkspace";
import CurriculumBrowser from "../features/curriculum/CurriculumBrowser";
import AssessmentBuilder from "../features/assessment/AssessmentBuilder";
import QuestionBankLibrary from "../features/question-bank/QuestionBankLibrary";
import type {
import DifferentiatedActivities from "../features/activities/DifferentiatedActivities";
import ScientificDiagrams from "../features/diagrams/ScientificDiagrams";
import CloudSources from "../features/cloud/CloudSources";
  AnswerKeyItem,
  EducationalAnalysisReport,
  EducationalQualityToolsReport,
  ApiConnectionStatus,
  AccountRole,
  AuthAccountPublic,
  AuthStatus,
  ExtractedTextInfo,
  InitialExtractionStatus,
  FullExamEndToEndReport,
  FullExamExportReport,
  FullExamIntakeReport,
  FullExamTranslationReport,
  GlossaryTerm,
  ProjectMetadata,
  PdfLayoutAssetInfo,
  ProjectReadinessReport,
  ProjectSession,
  QuestionItem,
  QuestionStatus,
  SchoolLogoInfo,
  UploadedFileInfo,
  TranslationProviderStatus,
  TranslationBatchSummary,
  VisualCropRequest,
} from "../types/project";

function sortQuestions(questions: QuestionItem[]) {
  return [...questions].sort((a, b) => a.orderIndex - b.orderIndex);
}


const ACTIVE_PROJECT_STORAGE_KEY = "madarik-active-project-id";


function applyProjectSession(
  project: ProjectSession,
  setters: {
    setProjectId: (projectId: string) => void;
    setMetadata: (metadata: ProjectMetadata) => void;
    setUploadedFile: (fileInfo: UploadedFileInfo | null) => void;
    setSchoolLogo: (schoolLogo: SchoolLogoInfo | null) => void;
    setExtractedText: (extractedText: ExtractedTextInfo | null) => void;
    setFullExamIntakeReport: (
      report: FullExamIntakeReport | null,
    ) => void;
    setFullExamTranslationReport: (
      report: FullExamTranslationReport | null,
    ) => void;
    setFullExamExportReport: (
      report: FullExamExportReport | null,
    ) => void;
    setFullExamEndToEndReport: (
      report: FullExamEndToEndReport | null,
    ) => void;
    setQuestions: (questions: QuestionItem[]) => void;
    setGlossary: (glossary: GlossaryTerm[]) => void;
    setLayoutAssets: (layoutAssets: PdfLayoutAssetInfo[]) => void;
    setAnswerKey: (answerKey: AnswerKeyItem[]) => void;
    setEducationalAnalysis: (
      analysis: EducationalAnalysisReport | null,
    ) => void;
    setQualityTools: (
      qualityTools: EducationalQualityToolsReport | null,
    ) => void;
    setTranslationBatchSummary: (
      summary: TranslationBatchSummary | null,
    ) => void;
  },
) {
  setters.setProjectId(project.id);
  setters.setMetadata(project.metadata);
  setters.setUploadedFile(project.uploadedFile);
  setters.setSchoolLogo(project.schoolLogo);
  setters.setExtractedText(project.extractedText);
  setters.setFullExamIntakeReport(project.fullExamIntakeReport ?? null);
  setters.setFullExamTranslationReport(
    project.fullExamTranslationReport ?? null,
  );
  setters.setFullExamExportReport(project.fullExamExportReport ?? null);
  setters.setFullExamEndToEndReport(
    project.fullExamEndToEndReport ?? null,
  );
  setters.setQuestions(project.questions);
  setters.setGlossary(project.glossary);
  setters.setLayoutAssets(project.layoutAssets);
  setters.setAnswerKey(project.answerKey);
  setters.setEducationalAnalysis(project.educationalAnalysis);
  setters.setQualityTools(project.qualityTools);
  setters.setTranslationBatchSummary(project.translationBatchSummary ?? null);
}

export function App() {
  const [activeIndex, setActiveIndex] = useState(0);
  const [workspaceMode, setWorkspaceMode] = useState<"home" | "quick" | "professional" | "curriculum" | "question-bank" | "assessment" | "differentiated-activities" | "scientific-diagrams" | "cloud-sources">("home");
  const [quickRunStatus, setQuickRunStatus] = useState<
    "idle" | "parsing" | "translating" | "checking" | "completed" | "error"
  >("idle");
  const [quickRunMessage, setQuickRunMessage] = useState(
    "ارفع ورقة اختبار علمية ثم شغّل الترجمة السريعة.",
  );

  const [projectId, setProjectId] = useState<string | null>(null);
  const [isProjectHydrating, setProjectHydrating] = useState(true);
  const [apiStatus, setApiStatus] = useState<ApiConnectionStatus>("connecting");
  const [lastSyncNote, setLastSyncNote] = useState(
    "يتم إنشاء جلسة مشروع مؤقتة...",
  );
  const [metadata, setMetadata] = useState<ProjectMetadata>(defaultMetadata);
  const [uploadedFile, setUploadedFile] = useState<UploadedFileInfo | null>(
    null,
  );
  const [schoolLogo, setSchoolLogo] = useState<SchoolLogoInfo | null>(null);
  const [extractedText, setExtractedText] = useState<ExtractedTextInfo | null>(
    null,
  );
  const [initialExtractionStatus, setInitialExtractionStatus] =
    useState<InitialExtractionStatus>({
      phase: "idle",
      startedAt: null,
      message: "بانتظار اختيار ملف.",
      canRetry: false,
    });
  const lastSelectedFileRef = useRef<File | null>(null);
  const [fullExamIntakeReport, setFullExamIntakeReport] =
    useState<FullExamIntakeReport | null>(null);
  const [fullExamTranslationReport, setFullExamTranslationReport] =
    useState<FullExamTranslationReport | null>(null);
  const [fullExamExportReport, setFullExamExportReport] =
    useState<FullExamExportReport | null>(null);
  const [fullExamEndToEndReport, setFullExamEndToEndReport] =
    useState<FullExamEndToEndReport | null>(null);
  const [questions, setQuestions] = useState<QuestionItem[]>(sampleQuestions);
  const [glossary, setGlossary] = useState<GlossaryTerm[]>(sampleGlossary);
  const [layoutAssets, setLayoutAssets] = useState<PdfLayoutAssetInfo[]>([]);
  const [answerKey, setAnswerKey] = useState<AnswerKeyItem[]>([]);
  const [educationalAnalysis, setEducationalAnalysis] =
    useState<EducationalAnalysisReport | null>(null);
  const [qualityTools, setQualityTools] =
    useState<EducationalQualityToolsReport | null>(null);
  const [translationProviderStatus, setTranslationProviderStatus] =
    useState<TranslationProviderStatus | null>(null);
  const [translationBatchSummary, setTranslationBatchSummary] =
    useState<TranslationBatchSummary | null>(null);
  const [projectReadiness, setProjectReadiness] =
    useState<ProjectReadinessReport | null>(null);
  const [projectLibrary, setProjectLibrary] = useState<ProjectSession[]>([]);
  const [isProjectLibraryLoading, setProjectLibraryLoading] = useState(false);
  const [authStatus, setAuthStatus] = useState<AuthStatus | null>(null);
  const [authAccount, setAuthAccount] = useState<AuthAccountPublic | null>(
    null,
  );
  const [authToken, setAuthToken] = useState<string | null>(() =>
    window.localStorage.getItem("madarik-auth-token"),
  );
  const [authMessage, setAuthMessage] = useState(
    "الحسابات اختيارية الآن، وستصبح أساس الصلاحيات لاحقًا.",
  );
  const [authAccounts, setAuthAccounts] = useState<AuthAccountPublic[]>([]);
  const [authAccountsLoading, setAuthAccountsLoading] = useState(false);
  const [isAuthPanelOpen, setAuthPanelOpen] = useState(false);
  const glossaryUpdateQueuesRef = useRef(
    new Map<string, Promise<void>>(),
  );
  const glossaryUpdateVersionsRef = useRef(
    new Map<string, number>(),
  );

  const activeStep = steps[activeIndex];
  const progressLabel = useMemo(
    () => `${activeIndex + 1} من ${steps.length}`,
    [activeIndex],
  );

  const approvedCount = questions.filter(
    (question) => question.status === "approved",
  ).length;
  const needsReviewCount = questions.filter(
    (question) => question.status === "needs_review",
  ).length;
  const canAdvanceFromStart = Boolean(extractedText?.text.trim());
  const applyProject = useCallback((project: ProjectSession) => {
    applyProjectSession(project, {
      setProjectId,
      setMetadata,
      setUploadedFile,
      setSchoolLogo,
      setExtractedText,
      setFullExamIntakeReport,
      setFullExamTranslationReport,
      setFullExamExportReport,
      setFullExamEndToEndReport,
      setQuestions,
      setGlossary: (serverGlossary) => {
        const pendingTermIds = new Set(
          glossaryUpdateQueuesRef.current.keys(),
        );
        setGlossary((currentGlossary) =>
          serverGlossary.map((serverTerm) => {
            if (!pendingTermIds.has(serverTerm.id)) return serverTerm;
            return (
              currentGlossary.find((term) => term.id === serverTerm.id) ??
              serverTerm
            );
          }),
        );
      },
      setLayoutAssets,
      setAnswerKey,
      setEducationalAnalysis,
      setQualityTools,
      setTranslationBatchSummary,
    });
    window.localStorage.setItem(ACTIVE_PROJECT_STORAGE_KEY, project.id);
  }, []);

  const hydrateProject = useCallback(
    (project: ProjectSession) => {
      setProjectHydrating(true);
      applyProject(project);
      setActiveIndex(getWorkflowStageIndex(project.currentStep));
      setProjectReadiness(null);

      window.requestAnimationFrame(() => {
        setProjectHydrating(false);
      });
    },
    [applyProject],
  );

  async function refreshAuthAccounts() {
    if (authAccount?.role !== "owner") {
      setAuthAccounts([]);
      return;
    }

    setAuthAccountsLoading(true);
    try {
      const accounts = await listAuthAccounts();
      setAuthAccounts(accounts);
      setAuthMessage(`تم تحديث قائمة الحسابات: ${accounts.length} حساب.`);
    } catch (error) {
      console.error(error);
      setAuthMessage("فشل تحديث قائمة الحسابات.");
    } finally {
      setAuthAccountsLoading(false);
    }
  }

  async function createManagedAccount(
    username: string,
    displayName: string,
    password: string,
    role: AccountRole,
  ) {
    try {
      await createAuthAccount({
        username,
        displayName,
        password,
        role,
        isActive: true,
      });
      const accounts = await listAuthAccounts();
      setAuthAccounts(accounts);
      setAuthMessage("تم إنشاء الحساب الجديد.");
    } catch (error) {
      console.error(error);
      setAuthMessage("فشل إنشاء الحساب. قد يكون اسم المستخدم مستخدمًا سابقًا.");
    }
  }

  async function toggleManagedAccount(accountId: string, isActive: boolean) {
    try {
      await updateAuthAccount(accountId, { isActive });
      const accounts = await listAuthAccounts();
      setAuthAccounts(accounts);
      setAuthMessage(isActive ? "تم تفعيل الحساب." : "تم تعطيل الحساب.");
    } catch (error) {
      console.error(error);
      setAuthMessage("فشل تحديث حالة الحساب.");
    }
  }

  async function refreshAuthStatus() {
    try {
      const status = await getAuthStatus();
      setAuthStatus(status);

      const storedToken = window.localStorage.getItem("madarik-auth-token");
      if (storedToken) {
        try {
          const account = await getCurrentAccount(storedToken);
          setAuthToken(storedToken);
          setAuthAccount(account);
          setAuthMessage(`تم استعادة جلسة الدخول: ${account.displayName}.`);
          if (account.role === "owner")
            listAuthAccounts()
              .then(setAuthAccounts)
              .catch((accountsError: unknown) => console.error(accountsError));
        } catch {
          window.localStorage.removeItem("madarik-auth-token");
          setAuthToken(null);
          setAuthAccount(null);
          setAuthMessage("انتهت جلسة الدخول السابقة أو لم تعد صالحة.");
        }
      }
    } catch (error) {
      console.error(error);
      setAuthMessage("تعذر قراءة حالة الحسابات من Backend.");
    }
  }

  async function bootstrapOwnerAccount(
    username: string,
    displayName: string,
    password: string,
  ) {
    try {
      const session = await bootstrapOwner(username, displayName, password);
      window.localStorage.setItem("madarik-auth-token", session.token);
      setAuthToken(session.token);
      setAuthAccount(session.account);
      setAuthStatus({ accountsExist: true, requiresBootstrap: false });
      setAuthMessage("تم إنشاء حساب مالك المنصة وتسجيل الدخول.");
      listAuthAccounts()
        .then(setAuthAccounts)
        .catch((accountsError: unknown) => console.error(accountsError));
      listProjects(50)
        .then(setProjectLibrary)
        .catch((libraryError: unknown) => console.error(libraryError));
    } catch (error) {
      console.error(error);
      setAuthMessage(
        "فشل إنشاء حساب المالك. ربما تم إنشاؤه سابقًا أو البيانات غير صالحة.",
      );
    }
  }

  async function loginAccount(username: string, password: string) {
    try {
      const session = await login(username, password);
      window.localStorage.setItem("madarik-auth-token", session.token);
      setAuthToken(session.token);
      setAuthAccount(session.account);
      setAuthMessage(`تم تسجيل الدخول: ${session.account.displayName}.`);
      if (session.account.role === "owner")
        listAuthAccounts()
          .then(setAuthAccounts)
          .catch((accountsError: unknown) => console.error(accountsError));
      listProjects(50)
        .then(setProjectLibrary)
        .catch((libraryError: unknown) => console.error(libraryError));
    } catch (error) {
      console.error(error);
      setAuthMessage(
        "فشل تسجيل الدخول. اسم المستخدم أو كلمة المرور غير صحيحة.",
      );
    }
  }

  async function logoutAccount() {
    if (authToken) {
      await logout(authToken).catch((error: unknown) => console.error(error));
    }
    window.localStorage.removeItem("madarik-auth-token");
    window.localStorage.removeItem(ACTIVE_PROJECT_STORAGE_KEY);
    setAuthToken(null);
    setAuthAccount(null);
    setAuthAccounts([]);
    setAuthMessage("تم تسجيل الخروج.");
    listProjects(50)
      .then(setProjectLibrary)
      .catch((libraryError: unknown) => console.error(libraryError));
  }

  async function refreshProjectLibrary() {
    if (apiStatus === "offline") {
      setLastSyncNote("لا يمكن تحديث مكتبة المشاريع دون اتصال Backend.");
      return;
    }

    setProjectLibraryLoading(true);
    try {
      const projects = await listProjects(50);
      setProjectLibrary(projects);
      setLastSyncNote(
        `تم تحديث مكتبة المشاريع: ${projects.length} مشروع محفوظ.`,
      );
    } catch (error) {
      console.error(error);
      setLastSyncNote("فشل تحديث مكتبة المشاريع المحفوظة.");
    } finally {
      setProjectLibraryLoading(false);
    }
  }

  async function openPersistedProject(projectIdToOpen: string) {
    if (apiStatus === "offline") {
      setLastSyncNote("لا يمكن فتح مشروع محفوظ دون اتصال Backend.");
      return;
    }

    setApiStatus("syncing");
    try {
      const project = await getProject(projectIdToOpen);
      hydrateProject(project);
      setApiStatus("connected");
      setLastSyncNote(`تم فتح المشروع المحفوظ: ${project.id.slice(0, 8)}.`);
    } catch (error) {
      console.error(error);
      setApiStatus("connected");
      setLastSyncNote("فشل فتح المشروع المحفوظ.");
    }
  }

  async function deletePersistedProject(projectIdToDelete: string) {
    const confirmed = window.confirm(
      "سيتم حذف المشروع المحفوظ من SQLite. هل تريد المتابعة؟",
    );
    if (!confirmed) return;

    if (apiStatus === "offline") {
      setLastSyncNote("لا يمكن حذف مشروع محفوظ دون اتصال Backend.");
      return;
    }

    setApiStatus("syncing");
    try {
      await deleteProject(projectIdToDelete);
      const projects = await listProjects(50);
      setProjectLibrary(projects);
      setApiStatus("connected");
      setLastSyncNote("تم حذف المشروع من مكتبة المشاريع المحفوظة.");
      if (projectIdToDelete === projectId) {
        window.localStorage.removeItem(ACTIVE_PROJECT_STORAGE_KEY);
        await bootstrapProject();
      }
    } catch (error) {
      console.error(error);
      setApiStatus("connected");
      setLastSyncNote("فشل حذف المشروع المحفوظ.");
    }
  }


  async function deletePersistedProjects(projectIdsToDelete: string[]) {
    const uniqueIds = [...new Set(projectIdsToDelete)];
    if (uniqueIds.length === 0) return;

    const confirmed = window.confirm(
      `سيتم حذف ${uniqueIds.length} مشروعًا محفوظًا. هل تريد المتابعة؟`,
    );
    if (!confirmed) return;

    if (apiStatus === "offline") {
      setLastSyncNote("لا يمكن حذف المشاريع دون اتصال Backend.");
      return;
    }

    setApiStatus("syncing");
    try {
      for (const projectIdToDelete of uniqueIds) {
        await deleteProject(projectIdToDelete);
      }

      const deletedCurrentProject = Boolean(
        projectId && uniqueIds.includes(projectId),
      );

      if (deletedCurrentProject) {
        window.localStorage.removeItem(ACTIVE_PROJECT_STORAGE_KEY);
        await bootstrapProject();
      } else {
        const projects = await listProjects(50);
        setProjectLibrary(projects);
        setApiStatus("connected");
      }

      setLastSyncNote(`تم حذف ${uniqueIds.length} مشروعًا من المكتبة.`);
    } catch (error) {
      console.error(error);
      setApiStatus("connected");
      setLastSyncNote("تعذر إكمال الحذف الجماعي للمشاريع.");
    }
  }

  const bootstrapProject = useCallback(async () => {
    setApiStatus("connecting");
    setProjectHydrating(true);
    setLastSyncNote("جاري استعادة مشروع العمل من Backend...");

    try {
      const providerStatus = await getTranslationProviderStatus();
      setTranslationProviderStatus(providerStatus);

      const storedProjectId = window.localStorage.getItem(
        ACTIVE_PROJECT_STORAGE_KEY,
      );

      if (storedProjectId) {
        try {
          const restoredProject = await getProject(storedProjectId);
          hydrateProject(restoredProject);
          setApiStatus("connected");
          setLastSyncNote(
            `تمت استعادة مشروع العمل: ${restoredProject.id.slice(0, 8)}`,
          );
          listProjects(50)
            .then(setProjectLibrary)
            .catch((libraryError: unknown) => console.error(libraryError));
          return;
        } catch (restoreError) {
          console.error(restoreError);
          window.localStorage.removeItem(ACTIVE_PROJECT_STORAGE_KEY);
        }
      }

      setLastSyncNote("لا يوجد مشروع نشط محفوظ. جاري إنشاء مشروع جديد...");

      const createdProject = await createProject(defaultMetadata);
      const hydratedProject = await loadDemoContent(createdProject.id);

      hydrateProject(hydratedProject);
      setApiStatus("connected");
      setLastSyncNote(`تم إنشاء مشروع جديد: ${hydratedProject.id.slice(0, 8)}`);

      listProjects(50)
        .then(setProjectLibrary)
        .catch((libraryError: unknown) => console.error(libraryError));
    } catch (error) {
      console.error(error);
      setProjectId(null);
      setMetadata(defaultMetadata);
      setUploadedFile(null);
      setSchoolLogo(null);
      setExtractedText(null);
      setFullExamIntakeReport(null);
      setFullExamTranslationReport(null);
      setFullExamExportReport(null);
      setFullExamEndToEndReport(null);
      setQuestions(sampleQuestions);
      setGlossary(sampleGlossary);
      setLayoutAssets([]);
      setAnswerKey([]);
      setEducationalAnalysis(null);
      setQualityTools(null);
      setTranslationBatchSummary(null);
      setTranslationProviderStatus({
        provider: "mock",
        configured: false,
        model: "",
        fallback: "mock",
      });
      setProjectHydrating(false);
      setApiStatus("offline");
      setLastSyncNote(
        "تعذر الاتصال بالخلفية. تعمل الواجهة ببيانات محلية مؤقتة.",
      );
    }
  }, [hydrateProject]);

  useEffect(() => {
    void bootstrapProject();
  }, [bootstrapProject]);

  useEffect(() => {
    void refreshAuthStatus();
  }, []);


  useEffect(() => {
    if (isProjectHydrating || !projectId || apiStatus === "offline") return;

    void updateProjectStep(
      projectId,
      getLegacyStepForStage(activeStep.key),
    ).catch(
      (error: unknown) => {
        console.error(error);
        setApiStatus("offline");
        setLastSyncNote("تعذرت مزامنة الخطوة الحالية مع Backend.");
      },
    );
  }, [activeStep.key, apiStatus, isProjectHydrating, projectId]);


function openQuickTranslation() {
  setWorkspaceMode("quick");
  setActiveIndex(0);
  setQuickRunStatus("idle");
  setQuickRunMessage("ارفع ورقة اختبار علمية ثم شغّل الترجمة السريعة.");
}

function openCloudSources() {
  setWorkspaceMode("cloud-sources");
}

function openScientificDiagrams() {
  setWorkspaceMode("scientific-diagrams");
}

function openDifferentiatedActivities() {
  setWorkspaceMode("differentiated-activities");
}

function openAssessmentBuilder() {
  setWorkspaceMode("assessment");
}

function openQuestionBank() {
  setWorkspaceMode("question-bank");
}

function openCurriculum() {
  setWorkspaceMode("curriculum");
}

function openProfessionalTranslation() {
  setWorkspaceMode("professional");
  setActiveIndex(0);
}

function returnToTaskHome() {
  setWorkspaceMode("home");
  setActiveIndex(0);
}


async function runQuickTranslationWorkflow() {
  if (!projectId || apiStatus === "offline") {
    setQuickRunStatus("error");
    setQuickRunMessage(
      "لا يمكن تشغيل الترجمة السريعة دون اتصال Backend.",
    );
    return;
  }

  if (!extractedText?.isTextBased) {
    setQuickRunStatus("error");
    setQuickRunMessage(
      "ارفع ملفًا وانتظر اكتمال استخراج النص قبل بدء الترجمة السريعة.",
    );
    return;
  }

  setApiStatus("syncing");
  setQuickRunStatus("parsing");
  setQuickRunMessage("جارٍ تقسيم الورقة إلى أسئلة وأجزاء ودرجات...");

  try {
    const parsedProject = await parseExtractedQuestions(projectId);
    applyProject(parsedProject);

    const activeParsedQuestions = parsedProject.questions.filter(
      (question) => question.status !== "deleted",
    );

    if (activeParsedQuestions.length === 0) {
      throw new Error("No active questions were parsed.");
    }

    setQuickRunStatus("translating");
    setQuickRunMessage(
      `تم اكتشاف ${activeParsedQuestions.length} سؤالًا. جارٍ تشغيل الترجمة العلمية...`,
    );

    const translatedProject = await translateProjectQuestions(projectId);
    applyProject(translatedProject);

    setQuickRunStatus("checking");
    setQuickRunMessage(
      "اكتملت الترجمة. جارٍ فحص الأسئلة والدرجات وحالة الجاهزية...",
    );

    const readinessReport = await getProjectReadiness(projectId);
    setProjectReadiness(readinessReport);
    setApiStatus("connected");
    setQuickRunStatus("completed");

    if (readinessReport.ready) {
      setQuickRunMessage(
        `اكتملت الترجمة السريعة بنجاح: ${readinessReport.translatedQuestionCount} سؤالًا مترجمًا، والورقة جاهزة للتصدير.`,
      );
    } else {
      setQuickRunMessage(
        `اكتملت الترجمة، لكن توجد ${readinessReport.issues.length} ملاحظة تحتاج مراجعة قبل التصدير.`,
      );
    }
  } catch (error) {
    console.error(error);
    setApiStatus("connected");
    setQuickRunStatus("error");
    setQuickRunMessage(
      "تعذر إكمال الترجمة السريعة. لم تُحذف البيانات، ويمكن فتح المراجعة الاحترافية لمعرفة موضع التعثر.",
    );
  }
}

function openQuickProfessionalReview() {
  setWorkspaceMode("professional");
  setActiveIndex(1);
}

function openQuickExport() {
  setWorkspaceMode("professional");
  setActiveIndex(2);
}

  function goNext() {
    setActiveIndex((current) => Math.min(current + 1, steps.length - 1));
  }

  function goPrevious() {
    setActiveIndex((current) => Math.max(current - 1, 0));
  }

  async function downloadProjectSnapshot() {
    if (!projectId || apiStatus === "offline") {
      setLastSyncNote("لا يمكن حفظ نسخة مشروع دون اتصال Backend.");
      return;
    }

    setApiStatus("syncing");
    try {
      const snapshot = await exportProjectSnapshot(projectId);
      const blob = new Blob([JSON.stringify(snapshot, null, 2)], {
        type: "application/json;charset=utf-8",
      });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      const safeTitle = (metadata.paperTitle || "madarik-project").replace(
        /[^A-Za-z0-9_-]+/g,
        "_",
      );
      link.href = url;
      link.download = `${safeTitle || "madarik-project"}_snapshot.json`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
      setApiStatus("connected");
      setLastSyncNote(
        "تم تنزيل نسخة JSON من مشروع العمل الحالي. احتفظ بها لاستكمال العمل لاحقًا.",
      );
    } catch (error) {
      console.error(error);
      setApiStatus("connected");
      setLastSyncNote("فشل تنزيل نسخة المشروع.");
    }
  }

  async function importProjectSnapshotFile(file: File | null) {
    if (!file) return;

    if (!file.name.toLowerCase().endsWith(".json")) {
      setLastSyncNote(
        "ملف الاستعادة يجب أن يكون JSON صادرًا من منصة مدارك، لا ملفًا مجهولًا جاء من ظلام الإنترنت.",
      );
      return;
    }

    if (apiStatus === "offline") {
      setLastSyncNote("لا يمكن استعادة مشروع دون اتصال Backend.");
      return;
    }

    setApiStatus("syncing");
    try {
      const rawText = await file.text();
      const snapshot = JSON.parse(rawText) as unknown;
      const project = await importProjectSnapshot(snapshot);
      hydrateProject(project);
      setApiStatus("connected");
      setLastSyncNote(
        `تم استيراد نسخة المشروع كجلسة جديدة: ${project.id.slice(0, 8)}`,
      );
    } catch (error) {
      console.error(error);
      setApiStatus("connected");
      setLastSyncNote(
        "فشل استيراد نسخة المشروع. تأكد أن الملف صادر من منصة مدارك ولم يتم العبث به كما يفعل البشر عادة.",
      );
    }
  }

  async function resetProject() {
    const confirmed = window.confirm(
      "سيتم مسح مشروع العمل الحالي فقط. هل تريد المتابعة؟",
    );
    if (!confirmed) return;

    if (projectId) {
      await deleteProject(projectId).catch((error: unknown) =>
        console.error(error),
      );
    }

    window.localStorage.removeItem(ACTIVE_PROJECT_STORAGE_KEY);
    setActiveIndex(0);
    await bootstrapProject();
  }

  function handleMetadataChange(nextMetadata: ProjectMetadata) {
    setMetadata(nextMetadata);

    if (!projectId || apiStatus === "offline") return;
    setApiStatus("syncing");
    updateProjectMetadata(projectId, nextMetadata)
      .then((project) => {
        applyProject(project);
        setApiStatus("connected");
        setLastSyncNote("تمت مزامنة بيانات الورقة مع Backend.");
      })
      .catch((error: unknown) => {
        console.error(error);
        setApiStatus("offline");
        setLastSyncNote("فشلت مزامنة بيانات الورقة. بقيت التعديلات محليًا.");
      });
  }

  async function handleLogoSelected(file: File | null) {
    if (!file) return;

    if (!projectId || apiStatus === "offline") {
      setLastSyncNote(
        "لا يمكن رفع الشعار دون اتصال Backend. الشعار يحتاج جلسة مؤقتة في الخلفية.",
      );
      return;
    }

    setApiStatus("syncing");
    try {
      const project = await uploadSchoolLogo(projectId, file);
      applyProject(project);
      setApiStatus("connected");
      setLastSyncNote("تم رفع شعار المدرسة وربطه بتصدير DOCX وPDF.");
    } catch (error) {
      console.error(error);
      setApiStatus("connected");
      setLastSyncNote(
        "فشل رفع الشعار. يدعم Phase 1-F3 ملفات PNG وJPG بحجم صغير.",
      );
    }
  }

  async function handleLogoRemove() {
    setSchoolLogo(null);

    if (!projectId || apiStatus === "offline") return;

    setApiStatus("syncing");
    try {
      const project = await deleteSchoolLogo(projectId);
      applyProject(project);
      setApiStatus("connected");
      setLastSyncNote("تم حذف شعار المدرسة من جلسة المشروع.");
    } catch (error) {
      console.error(error);
      setApiStatus("connected");
      setLastSyncNote("فشل حذف الشعار من Backend. بقي الحذف محليًا فقط.");
    }
  }

  function handleFileSelected(file: File | null) {
    if (!file) {
      lastSelectedFileRef.current = null;
      setInitialExtractionStatus({
        phase: "idle",
        startedAt: null,
        message: "بانتظار اختيار ملف.",
        canRetry: false,
      });
      setUploadedFile(null);
      setExtractedText(null);
      setFullExamIntakeReport(null);
      setFullExamTranslationReport(null);
      setFullExamExportReport(null);
      setFullExamEndToEndReport(null);

      if (!projectId || apiStatus === "offline") return;
      setApiStatus("syncing");
      setUploadedFileInfo(projectId, null)
        .then((project) => {
          applyProject(project);
          setApiStatus("connected");
          setLastSyncNote("تمت إزالة الملف ونتيجة الاستخراج من الجلسة.");
        })
        .catch((error: unknown) => {
          console.error(error);
          setApiStatus("offline");
          setLastSyncNote(
            "فشلت إزالة معلومات الملف من Backend. بقيت الحالة محليًا.",
          );
        });
      return;
    }

    lastSelectedFileRef.current = file;
    const startedAt = Date.now();
    const fileInfo: UploadedFileInfo = {
      name: file.name,
      size: file.size,
      type: file.type || "غير معروف",
    };
    setInitialExtractionStatus({
      phase: "uploading",
      startedAt,
      message: "تم اختيار الملف. جارٍ إرساله وبدء القراءة الأولية...",
      canRetry: false,
    });
    setUploadedFile(fileInfo);
    setExtractedText(null);
    setLayoutAssets([]);
    setFullExamIntakeReport(null);
    setFullExamTranslationReport(null);
    setFullExamExportReport(null);
    setFullExamEndToEndReport(null);

    if (!projectId || apiStatus === "offline") {
      const isGithubPagesPreview =
        window.location.hostname.endsWith(".github.io");

      setInitialExtractionStatus({
        phase: "error",
        startedAt,
        message: isGithubPagesPreview
          ? "هذه نسخة معاينة على GitHub Pages. رفع الملف يعمل محليًا، لكن قراءة النص تحتاج Backend مستضافًا."
          : "تعذر بدء القراءة لأن Backend غير متصل.",
        canRetry: true,
      });
      setLastSyncNote(
        isGithubPagesPreview
          ? "وضع المعاينة: يمكنك فحص التصميم والسحب والإفلات، لكن الاستخراج والترجمة والقص تحتاج Backend."
          : "تم اختيار الملف محليًا فقط. لا يمكن استخراج النص دون اتصال Backend.",
      );
      return;
    }

    const isImageFile =
      file.type.startsWith("image/") || /\.(png|jpe?g|webp)$/i.test(file.name);
    const isPdfFile =
      file.type === "application/pdf" ||
      file.name.toLowerCase().endsWith(".pdf");

    if (!isImageFile && !isPdfFile) {
      setInitialExtractionStatus({
        phase: "error",
        startedAt,
        message: "نوع الملف غير مدعوم للاستخراج الأولي.",
        canRetry: false,
      });
      setExtractedText({
        text: "",
        preview: "",
        pageCount: 0,
        characterCount: 0,
        isTextBased: false,
        message:
          "يدعم المسار ملفات PDF النصية أو المصوّرة وصور PNG/JPG/WEBP فقط.",
      });
      setLastSyncNote("نوع الملف غير مدعوم في هذه المرحلة.");
      return;
    }

    setApiStatus("syncing");
    setInitialExtractionStatus({
      phase: isImageFile ? "ocr" : "reading",
      startedAt,
      message: isImageFile
        ? "جارٍ تشغيل OCR على الصورة..."
        : "جارٍ قراءة النص القابل للتحديد من PDF...",
      canRetry: false,
    });

    const extractionRequest = isImageFile
      ? uploadImageAndExtractText(projectId, file)
      : uploadPdfAndExtractText(projectId, file).then((project) => {
          if (project.extractedText?.isTextBased) return project;
          setInitialExtractionStatus({
            phase: "ocr",
            startedAt,
            message: "الملف مصوّر. جارٍ تشغيل OCR دون تحليل الرسوم الآن...",
            canRetry: false,
          });
          return uploadPdfOcrAndExtractText(projectId, file);
        });

    extractionRequest
      .then((project) => {
        applyProject(project);
        setApiStatus("connected");
        const elapsedSeconds = Math.max(1, Math.round((Date.now() - startedAt) / 1000));
        setInitialExtractionStatus({
          phase: "success",
          startedAt,
          message: `اكتملت القراءة الأولية خلال ${elapsedSeconds} ث. تحليل الرسوم مؤجل للمراجعة.`,
          canRetry: false,
        });
        setLastSyncNote(
          `${project.extractedText?.message ?? "تم رفع الملف واستخراج النص."} لم يبدأ تحليل التخطيط أو القص أثناء القراءة الأولية.`,
        );
      })
      .catch((error: unknown) => {
        console.error(error);
        setApiStatus("connected");
        setUploadedFile(fileInfo);
        setInitialExtractionStatus({
          phase: "error",
          startedAt,
          message: isImageFile
            ? "تعذر OCR للصورة. جرّب صورة أوضح أو أعد المحاولة."
            : "تعذر استخراج النص. جرّب إعادة المحاولة أو ملفًا أوضح.",
          canRetry: true,
        });
        setExtractedText({
          text: "",
          preview: "",
          pageCount: 0,
          characterCount: 0,
          isTextBased: false,
          message: isImageFile
            ? "تعذر تشغيل OCR على الصورة. جرّب صورة أوضح أو قصّ منطقة السؤال فقط."
            : "تعذر استخراج النص من PDF نصيًا أو عبر OCR مبدئي. تأكد من جودة الملف أو جرّب صورة واضحة.",
        });
        setLastSyncNote(
          isImageFile
            ? "فشل OCR المبدئي للصورة."
            : "فشل استخراج النص من PDF نصيًا وOCR.",
        );
      });
  }

  function retryInitialExtraction() {
    if (lastSelectedFileRef.current) {
      handleFileSelected(lastSelectedFileRef.current);
    }
  }

  async function handleLayoutAssetDelete(assetId: string) {
    if (!projectId || apiStatus === "offline") {
      setLastSyncNote("لا يمكن حذف لقطة التخطيط دون اتصال Backend.");
      return;
    }

    setApiStatus("syncing");
    try {
      const project = await deletePdfLayoutAsset(projectId, assetId);
      applyProject(project);
      setApiStatus("connected");
      setLastSyncNote("تم حذف لقطة التخطيط من المشروع.");
    } catch (error) {
      console.error(error);
      setApiStatus("connected");
      setLastSyncNote("فشل حذف لقطة التخطيط.");
    }
  }

  async function bulkUpdateReviewStatus(
    status: QuestionStatus,
    includeDeleted = false,
  ) {
    if (!projectId || apiStatus === "offline") {
      setLastSyncNote("لا يمكن تنفيذ إجراء جماعي دون اتصال Backend.");
      return;
    }

    setApiStatus("syncing");
    try {
      const project = await bulkUpdateQuestionStatus(
        projectId,
        status,
        includeDeleted,
      );
      applyProject(project);
      setProjectReadiness(null);
      setApiStatus("connected");
      const label =
        status === "approved"
          ? "معتمد"
          : status === "needs_review"
            ? "يحتاج مراجعة"
            : "محذوف";
      setLastSyncNote(`تم تحديث حالة الأسئلة جماعيًا إلى: ${label}.`);
    } catch (error) {
      console.error(error);
      setApiStatus("connected");
      setLastSyncNote("فشل تنفيذ الإجراء الجماعي على الأسئلة.");
    }
  }

  async function handleQuestionAssetUpload(questionId: string, file: File) {
    if (!projectId || apiStatus === "offline") {
      setLastSyncNote(
        "لا يمكن ربط مرفق بالسؤال دون اتصال Backend. المرفقات تُحفظ مؤقتًا في الخلفية.",
      );
      return;
    }

    setApiStatus("syncing");
    try {
      const project = await uploadQuestionAsset(projectId, questionId, file);
      applyProject(project);
      setApiStatus("connected");
      setLastSyncNote(
        "تم ربط الصورة/الجدول ببطاقة السؤال وسيظهر في DOCX وPDF.",
      );
    } catch (error) {
      console.error(error);
      setApiStatus("connected");
      setLastSyncNote(
        "فشل رفع مرفق السؤال. يدعم Phase 1-H1 صور PNG وJPG بحجم لا يتجاوز 2MB.",
      );
    }
  }

  async function handleQuestionAssetDelete(
    questionId: string,
    assetId: string,
  ) {
    if (!projectId || apiStatus === "offline") {
      setLastSyncNote("لا يمكن حذف المرفق دون اتصال Backend.");
      return;
    }

    setApiStatus("syncing");
    try {
      const project = await deleteQuestionAsset(projectId, questionId, assetId);
      applyProject(project);
      setApiStatus("connected");
      setLastSyncNote("تم حذف مرفق السؤال من الجلسة المؤقتة.");
    } catch (error) {
      console.error(error);
      setApiStatus("connected");
      setLastSyncNote("فشل حذف مرفق السؤال.");
    }
  }

  async function handleQuestionLayoutAssetLink(
    questionId: string,
    assetId: string,
  ) {
    if (!projectId || apiStatus === "offline") {
      setLastSyncNote(
        "\u0644\u0627 \u064a\u0645\u0643\u0646 \u0631\u0628\u0637 \u0644\u0642\u0637\u0629 PDF \u062f\u0648\u0646 \u0627\u062a\u0635\u0627\u0644 Backend.",
      );
      return;
    }

    setApiStatus("syncing");

    try {
      const project = await linkQuestionLayoutAsset(
        projectId,
        questionId,
        assetId,
      );

      applyProject(project);
      setApiStatus("connected");
      setLastSyncNote(
        "\u062a\u0645 \u0631\u0628\u0637 \u0644\u0642\u0637\u0629 PDF \u0628\u0627\u0644\u0633\u0624\u0627\u0644.",
      );
    } catch (error) {
      console.error(error);
      setApiStatus("connected");
      setLastSyncNote(
        "\u0641\u0634\u0644 \u0631\u0628\u0637 \u0644\u0642\u0637\u0629 PDF \u0628\u0627\u0644\u0633\u0624\u0627\u0644.",
      );
    }
  }

  async function handleQuestionLayoutAssetUnlink(
    questionId: string,
    assetId: string,
  ) {
    if (!projectId || apiStatus === "offline") {
      setLastSyncNote(
        "\u0644\u0627 \u064a\u0645\u0643\u0646 \u0641\u0643 \u0631\u0628\u0637 \u0644\u0642\u0637\u0629 PDF \u062f\u0648\u0646 \u0627\u062a\u0635\u0627\u0644 Backend.",
      );
      return;
    }

    setApiStatus("syncing");

    try {
      const project = await unlinkQuestionLayoutAsset(
        projectId,
        questionId,
        assetId,
      );

      applyProject(project);
      setApiStatus("connected");
      setLastSyncNote(
        "\u062a\u0645 \u0641\u0643 \u0631\u0628\u0637 \u0644\u0642\u0637\u0629 PDF \u0639\u0646 \u0627\u0644\u0633\u0624\u0627\u0644.",
      );
    } catch (error) {
      console.error(error);
      setApiStatus("connected");
      setLastSyncNote(
        "\u0641\u0634\u0644 \u0641\u0643 \u0631\u0628\u0637 \u0644\u0642\u0637\u0629 PDF \u0639\u0646 \u0627\u0644\u0633\u0624\u0627\u0644.",
      );
    }
  }


  async function handleQuestionLayoutAssetCrop(
    questionId: string,
    assetId: string,
    crop: VisualCropRequest,
  ) {
    if (!projectId || apiStatus === "offline") {
      setLastSyncNote(
        "لا يمكن قص عنصر بصري دون اتصال Backend.",
      );
      throw new Error("Backend is unavailable.");
    }

    setApiStatus("syncing");

    try {
      const project = await cropQuestionLayoutAsset(
        projectId,
        questionId,
        assetId,
        crop,
      );

      applyProject(project);
      setApiStatus("connected");
      setLastSyncNote(
        "تم قص العنصر البصري وحفظه داخل مرفقات السؤال.",
      );
    } catch (error) {
      console.error(error);
      setApiStatus("connected");
      setLastSyncNote(
        "فشل قص العنصر البصري. لم تتغير مرفقات السؤال.",
      );
      throw error;
    }
  }


  function updateQuestion(questionId: string, updates: Partial<QuestionItem>) {
    setQuestions((currentQuestions) =>
      currentQuestions.map((question) =>
        question.id === questionId ? { ...question, ...updates } : question,
      ),
    );
    setProjectReadiness(null);
    setFullExamTranslationReport(null);
    setFullExamExportReport(null);
    setFullExamEndToEndReport(null);

    if (!projectId || apiStatus === "offline") return;
    setApiStatus("syncing");
    updateQuestionOnServer(projectId, questionId, updates)
      .then((project) => {
        applyProject(project);
        setApiStatus("connected");
        setLastSyncNote("تمت مزامنة بطاقة السؤال مع Backend.");
      })
      .catch((error: unknown) => {
        console.error(error);
        setApiStatus("offline");
        setLastSyncNote("فشلت مزامنة بطاقة السؤال. بقي التعديل محليًا.");
      });
  }

  function moveQuestion(questionId: string, direction: "up" | "down") {
    setQuestions((currentQuestions) => {
      const movableQuestions = sortQuestions(currentQuestions).filter(
        (question) => question.status !== "deleted",
      );
      const currentPosition = movableQuestions.findIndex(
        (question) => question.id === questionId,
      );
      const targetPosition =
        direction === "up" ? currentPosition - 1 : currentPosition + 1;

      if (
        currentPosition < 0 ||
        targetPosition < 0 ||
        targetPosition >= movableQuestions.length
      ) {
        return currentQuestions;
      }

      const currentQuestion = movableQuestions[currentPosition];
      const targetQuestion = movableQuestions[targetPosition];
      const nextQuestions = currentQuestions.map((question) => {
        if (question.id === currentQuestion.id)
          return { ...question, orderIndex: targetQuestion.orderIndex };
        if (question.id === targetQuestion.id)
          return { ...question, orderIndex: currentQuestion.orderIndex };
        return question;
      });

      if (projectId && apiStatus !== "offline") {
        const orderedQuestionIds = sortQuestions(nextQuestions).map(
          (question) => question.id,
        );
        setApiStatus("syncing");
        reorderQuestions(projectId, orderedQuestionIds)
          .then((project) => {
            applyProject(project);
            setApiStatus("connected");
            setLastSyncNote("تمت مزامنة ترتيب الأسئلة مع Backend.");
          })
          .catch((error: unknown) => {
            console.error(error);
            setApiStatus("offline");
            setLastSyncNote("فشلت مزامنة ترتيب الأسئلة. بقي الترتيب محليًا.");
          });
      }

      return nextQuestions;
    });
  }

  function updateGlossaryTerm(termId: string, updates: Partial<GlossaryTerm>) {
    setGlossary((currentGlossary) =>
      currentGlossary.map((term) =>
        term.id === termId ? { ...term, ...updates } : term,
      ),
    );
    setFullExamTranslationReport(null);
    setFullExamExportReport(null);
    setFullExamEndToEndReport(null);

    if (!projectId || apiStatus === "offline") return;

    const version =
      (glossaryUpdateVersionsRef.current.get(termId) ?? 0) + 1;
    glossaryUpdateVersionsRef.current.set(termId, version);

    const previousQueue =
      glossaryUpdateQueuesRef.current.get(termId) ?? Promise.resolve();

    const queuedUpdate: Promise<void> = previousQueue
      .catch(() => undefined)
      .then(async () => {
        setApiStatus("syncing");
        const project = await updateGlossaryTermOnServer(
          projectId,
          termId,
          updates,
        );

        if (glossaryUpdateVersionsRef.current.get(termId) !== version) {
          return;
        }

        const savedTerm = project.glossary.find(
          (term) => term.id === termId,
        );
        if (savedTerm) {
          setGlossary((currentGlossary) =>
            currentGlossary.map((term) =>
              term.id === termId ? savedTerm : term,
            ),
          );
        }

        setFullExamTranslationReport(
          project.fullExamTranslationReport ?? null,
        );
        setFullExamExportReport(project.fullExamExportReport ?? null);
        setFullExamEndToEndReport(
          project.fullExamEndToEndReport ?? null,
        );
        setApiStatus("connected");
        setLastSyncNote("تم حفظ حالة مصطلح القاموس.");
      })
      .catch((error: unknown) => {
        console.error(error);
        if (glossaryUpdateVersionsRef.current.get(termId) === version) {
          setApiStatus("connected");
          setLastSyncNote(
            "تعذر حفظ مصطلح القاموس. بقي الاختيار ظاهرًا محليًا ولم يُعتمد في الخادم.",
          );
        }
      })
      .finally(() => {
        if (glossaryUpdateQueuesRef.current.get(termId) === queuedUpdate) {
          glossaryUpdateQueuesRef.current.delete(termId);
        }
      });

    glossaryUpdateQueuesRef.current.set(termId, queuedUpdate);
  }

  async function approveAllCompletedGlossaryTerms() {
    if (!projectId || apiStatus === "offline") {
      setLastSyncNote("لا يمكن اعتماد القاموس جماعيًا دون اتصال Backend.");
      return;
    }

    const termsToApprove = glossary.filter(
      (term) =>
        term.status === "needs_review" &&
        term.englishTerm.trim().length > 0 &&
        term.arabicTerm.trim().length > 0,
    );

    if (termsToApprove.length === 0) {
      setLastSyncNote("لا توجد مصطلحات مكتملة تنتظر الاعتماد.");
      return;
    }

    setApiStatus("syncing");
    try {
      let latestProject: ProjectSession | null = null;
      for (const term of termsToApprove) {
        latestProject = await updateGlossaryTermOnServer(
          projectId,
          term.id,
          { status: "approved" },
        );
      }

      if (latestProject) applyProject(latestProject);
      setApiStatus("connected");
      setLastSyncNote(
        `تم اعتماد ${termsToApprove.length} مصطلحًا مكتملًا دفعة واحدة.`,
      );
    } catch (error) {
      console.error(error);
      setApiStatus("connected");
      setLastSyncNote(
        "تعذر إكمال الاعتماد الجماعي للقاموس. بقيت المصطلحات غير المحفوظة للمراجعة.",
      );
    }
  }

  async function parseQuestionsFromExtractedText() {
    if (!projectId || apiStatus === "offline") {
      setLastSyncNote(
        "لا يمكن تقسيم النص دون اتصال Backend. النص موجود، لكن المحلل في الخلفية وليس في الواجهة.",
      );
      return;
    }

    if (!extractedText?.isTextBased) {
      setLastSyncNote(
        "ارفع PDF نصيًا أولًا قبل تحويل النص إلى أسئلة. لا نحلل الهواء، رغم أن بعض الاجتماعات تفعل ذلك.",
      );
      return;
    }

    setApiStatus("syncing");
    try {
      const project = await parseExtractedQuestions(projectId);
      applyProject(project);
      setApiStatus("connected");
      const intakeReport = project.fullExamIntakeReport;
      setLastSyncNote(
        intakeReport
          ? `تم تحويل الورقة إلى ${project.questions.length} بطاقة سؤال. حالة القبول الهيكلي: ${intakeReport.status}.`
          : `تم تحويل النص إلى ${project.questions.length} بطاقة سؤال تحتاج مراجعة.`,
      );
    } catch (error) {
      console.error(error);
      setApiStatus("connected");
      setLastSyncNote(
        "فشل تقسيم النص إلى أسئلة. قد يحتاج الملف إلى تنسيق أوضح أو OCR لاحقًا.",
      );
    }
  }

  async function translateQuestions() {
    if (!projectId || apiStatus === "offline") {
      setLastSyncNote(
        "لا يمكن تشغيل ترجمة الأسئلة دون اتصال Backend. المترجم موجود في الخلفية، لا في عالم الخيال.",
      );
      return;
    }

    if (
      questions.filter((question) => question.status !== "deleted").length === 0
    ) {
      setLastSyncNote(
        "لا توجد أسئلة نشطة قابلة للترجمة. حذف كل شيء ثم طلب الترجمة رياضة ذهنية غريبة.",
      );
      return;
    }

    setApiStatus("syncing");
    try {
      const project = await translateProjectQuestions(projectId);
      applyProject(project);
      setApiStatus("connected");
      setActiveIndex(1);
      const summary = project.translationBatchSummary;
      setLastSyncNote(
        summary
          ? (
              `اكتملت دفعة الترجمة: ${summary.totalItems} عنصرًا، ` +
              `نجاح خارجي ${summary.externalSuccessCount + summary.correctedSuccessCount}، ` +
              `fallback محلي ${summary.localFallbackCount}، ` +
              `فشل محفوظ بأمان ${summary.failedSafelyCount}.`
            )
          : "اكتملت الترجمة، لكن ملخص الدفعة غير متاح.",
      );
    } catch (error) {
      console.error(error);
      setApiStatus("connected");
      setLastSyncNote(
        "تعذر تشغيل ترجمة الأسئلة وأجزائها. تحقق من وجود أسئلة محللة ثم أعد المحاولة.",
      );
    }
  }

  async function retryQuestionTranslationForReview(
    questionId: string,
  ) {
    if (!projectId || apiStatus === "offline") {
      setLastSyncNote(
        "لا يمكن إعادة ترجمة السؤال دون اتصال Backend.",
      );
      return;
    }

    setApiStatus("syncing");
    try {
      const project = await retryQuestionTranslation(
        projectId,
        questionId,
      );
      applyProject(project);
      setApiStatus("connected");
      const report = project.fullExamTranslationReport;
      setLastSyncNote(
        report
          ? (
              `أعيدت ترجمة السؤال. اكتمال الورقة ${report.completionPercent}%، ` +
              `والأسئلة الفاشلة ${report.failedQuestions}.`
            )
          : "أعيدت ترجمة السؤال، لكن تقرير القبول غير متاح.",
      );
    } catch (error) {
      console.error(error);
      setApiStatus("connected");
      setLastSyncNote(
        "تعذرت إعادة ترجمة السؤال منفردًا. بقيت بقية الورقة دون تغيير.",
      );
    }
  }

  async function generateGlossaryFromQuestionCards() {
    if (!projectId || apiStatus === "offline") {
      setLastSyncNote(
        "لا يمكن توليد قاموس حقيقي دون اتصال Backend. القاموس الحالي محلي فقط.",
      );
      return;
    }

    if (questions.length === 0) {
      setLastSyncNote(
        "لا توجد أسئلة يمكن استخراج مصطلحات منها. نحتاج مادة خام، لا نقرأ النوايا.",
      );
      return;
    }

    setApiStatus("syncing");
    try {
      const project = await generateGlossaryFromQuestions(projectId);
      applyProject(project);
      setApiStatus("connected");
      setLastSyncNote(
        `تم توليد ${project.glossary.length} مصطلحًا من بطاقات الأسئلة.`,
      );
    } catch (error) {
      console.error(error);
      setApiStatus("connected");
      setLastSyncNote(
        "فشل توليد قاموس الورقة. قد لا تحتوي الأسئلة على مصطلحات ضمن القاموس الأولي.",
      );
    }
  }

  async function refreshProjectReadiness() {
    if (!projectId || apiStatus === "offline") {
      setProjectReadiness(null);
      setLastSyncNote("لا يمكن فحص الجاهزية دون اتصال Backend.");
      return;
    }

    setApiStatus("syncing");
    try {
      const report = await getProjectReadiness(projectId);
      setProjectReadiness(report);
      setApiStatus("connected");
      setLastSyncNote(
        report.ready
          ? "فحص الجاهزية: الورقة قابلة للتصدير."
          : "فحص الجاهزية: توجد ملاحظات قبل التصدير.",
      );
    } catch (error) {
      console.error(error);
      setApiStatus("connected");
      setLastSyncNote("تعذر فحص جاهزية التصدير.");
    }
  }

  async function generateProjectQualityTools() {
    if (!projectId || apiStatus === "offline") {
      setLastSyncNote("لا يمكن توليد أدوات الجودة دون اتصال Backend.");
      return;
    }

    setApiStatus("syncing");
    try {
      const project = await generateQualityTools(projectId);
      applyProject(project);
      setApiStatus("connected");
      setLastSyncNote(
        "تم توليد أدوات الجودة التربوية: Pareto وRadar وFishbone.",
      );
    } catch (error) {
      console.error(error);
      setApiStatus("connected");
      setLastSyncNote("فشل توليد أدوات الجودة. تأكد من وجود أسئلة نشطة.");
    }
  }

  async function clearProjectQualityTools() {
    if (!projectId || apiStatus === "offline") {
      setLastSyncNote("لا يمكن حذف أدوات الجودة دون اتصال Backend.");
      return;
    }

    setApiStatus("syncing");
    try {
      const project = await clearQualityTools(projectId);
      applyProject(project);
      setApiStatus("connected");
      setLastSyncNote("تم حذف أدوات الجودة.");
    } catch (error) {
      console.error(error);
      setApiStatus("connected");
      setLastSyncNote("فشل حذف أدوات الجودة.");
    }
  }

  async function generateProjectEducationalAnalysis() {
    if (!projectId || apiStatus === "offline") {
      setLastSyncNote("لا يمكن توليد التحليل التربوي دون اتصال Backend.");
      return;
    }

    setApiStatus("syncing");
    try {
      const project = await generateEducationalAnalysis(projectId);
      applyProject(project);
      setApiStatus("connected");
      setLastSyncNote("تم توليد التحليل التربوي التأسيسي للورقة.");
    } catch (error) {
      console.error(error);
      setApiStatus("connected");
      setLastSyncNote("فشل توليد التحليل التربوي. تأكد من وجود أسئلة نشطة.");
    }
  }

  async function clearProjectEducationalAnalysis() {
    if (!projectId || apiStatus === "offline") {
      setLastSyncNote("لا يمكن حذف التحليل التربوي دون اتصال Backend.");
      return;
    }

    setApiStatus("syncing");
    try {
      const project = await clearEducationalAnalysis(projectId);
      applyProject(project);
      setApiStatus("connected");
      setLastSyncNote("تم حذف التحليل التربوي.");
    } catch (error) {
      console.error(error);
      setApiStatus("connected");
      setLastSyncNote("فشل حذف التحليل التربوي.");
    }
  }

  async function generateProjectAnswerKey() {
    if (!projectId || apiStatus === "offline") {
      setLastSyncNote("لا يمكن توليد مسودة نموذج الإجابة دون اتصال Backend.");
      return;
    }

    setApiStatus("syncing");
    try {
      const project = await generateAnswerKeyDraft(projectId);
      applyProject(project);
      setApiStatus("connected");
      setLastSyncNote(
        `تم توليد مسودة نموذج إجابة لعدد ${project.answerKey.length} سؤال. راجعها قبل أي استخدام، طبعًا، لأن الآلة لا تملك رخصة تدريس.`,
      );
    } catch (error) {
      console.error(error);
      setApiStatus("connected");
      setLastSyncNote(
        "فشل توليد مسودة نموذج الإجابة. تأكد من وجود أسئلة نشطة.",
      );
    }
  }

  async function clearProjectAnswerKey() {
    if (!projectId || apiStatus === "offline") {
      setLastSyncNote("لا يمكن حذف مسودة نموذج الإجابة دون اتصال Backend.");
      return;
    }

    setApiStatus("syncing");
    try {
      const project = await clearAnswerKey(projectId);
      applyProject(project);
      setApiStatus("connected");
      setLastSyncNote("تم حذف مسودة نموذج الإجابة.");
    } catch (error) {
      console.error(error);
      setApiStatus("connected");
      setLastSyncNote("فشل حذف مسودة نموذج الإجابة.");
    }
  }

  async function runFullExamAcceptanceGate() {
    if (!projectId || apiStatus === "offline") {
      setLastSyncNote(
        "لا يمكن تشغيل بوابة القبول الشامل دون اتصال Backend.",
      );
      return;
    }

    setApiStatus("syncing");
    setLastSyncNote(
      "جاري تشغيل بوابة القبول الشامل وفحص ملفات Word وPDF في الذاكرة...",
    );

    try {
      const project = await runFullExamEndToEndAcceptance(projectId);
      applyProject(project);
      const readinessReport = await getProjectReadiness(projectId);
      setProjectReadiness(readinessReport);
      setApiStatus("connected");

      const gateStatus = project.fullExamEndToEndReport?.status;
      setLastSyncNote(
        gateStatus === "accepted"
          ? "بوابة القبول الشامل: المسار الكامل مقبول."
          : gateStatus === "needs_review"
            ? "بوابة القبول الشامل: توجد مراحل تحتاج مراجعة."
            : "بوابة القبول الشامل: توجد ملاحظات مانعة أو فشل في مرحلة.",
      );
    } catch (error) {
      console.error(error);
      setApiStatus("connected");
      setLastSyncNote("تعذر تشغيل بوابة القبول الشامل.");
      throw error;
    }
  }

  async function exportDocx() {
    if (!projectId || apiStatus === "offline") {
      setLastSyncNote(
        "لا يمكن إنشاء DOCX دون اتصال Backend. ملف Word يحتاج محرك التصدير في الخلفية.",
      );
      return;
    }

    const report = await getProjectReadiness(projectId);
    setProjectReadiness(report);
    if (!report.ready) {
      setLastSyncNote(
        "فحص الجاهزية منع تصدير Word حتى معالجة الملاحظات المانعة.",
      );
      return;
    }

    setApiStatus("syncing");
    try {
      const blob = await exportProjectDocx(projectId);
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      const safeTitle = (metadata.paperTitle || "madarik-export").replace(
        /[^A-Za-z0-9_-]+/g,
        "_",
      );
      link.download = `${safeTitle || "madarik-export"}.docx`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
      const refreshedProject = await getProject(projectId);
      applyProject(refreshedProject);
      setApiStatus("connected");
      setLastSyncNote("تم إنشاء ملف Word وتحديث تقرير قبول التصدير.");
    } catch (error) {
      console.error(error);
      setApiStatus("connected");
      setLastSyncNote(
        "فشل إنشاء ملف Word. تحقق من وجود أسئلة نشطة ثم أعد المحاولة.",
      );
      throw error;
    }
  }

  async function exportPdf() {
    if (!projectId || apiStatus === "offline") {
      setLastSyncNote(
        "لا يمكن إنشاء PDF دون اتصال Backend. ملف PDF يحتاج محرك التصدير في الخلفية.",
      );
      return;
    }

    const report = await getProjectReadiness(projectId);
    setProjectReadiness(report);
    if (!report.ready) {
      setLastSyncNote(
        "فحص الجاهزية منع تصدير PDF حتى معالجة الملاحظات المانعة.",
      );
      return;
    }

    setApiStatus("syncing");
    try {
      const blob = await exportProjectPdf(projectId);
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      const safeTitle = (metadata.paperTitle || "madarik-export").replace(
        /[^A-Za-z0-9_-]+/g,
        "_",
      );
      link.download = `${safeTitle || "madarik-export"}.pdf`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
      const refreshedProject = await getProject(projectId);
      applyProject(refreshedProject);
      setApiStatus("connected");
      setLastSyncNote("تم إنشاء ملف PDF وتحديث تقرير قبول التصدير.");
    } catch (error) {
      console.error(error);
      setApiStatus("connected");
      setLastSyncNote(
        "فشل إنشاء ملف PDF. تحقق من وجود أسئلة نشطة ثم أعد المحاولة.",
      );
      throw error;
    }
  }

  async function reloadDemoFromBackend() {
    if (!projectId || apiStatus === "offline") {
      setQuestions(sampleQuestions);
      setGlossary(sampleGlossary);
      setLayoutAssets([]);
      setTranslationBatchSummary(null);
      setFullExamIntakeReport(null);
      setFullExamTranslationReport(null);
      setFullExamExportReport(null);
      setFullExamEndToEndReport(null);
      setLastSyncNote("تمت إعادة تحميل البيانات التجريبية محليًا.");
      return;
    }

    setApiStatus("syncing");
    try {
      const project = await loadDemoContent(projectId);
      applyProject(project);
      setApiStatus("connected");
      setLastSyncNote("تم تحميل الأسئلة والقاموس التجريبيين من Backend.");
    } catch (error) {
      console.error(error);
      setApiStatus("offline");
      setLastSyncNote("فشل تحميل البيانات التجريبية من Backend.");
    }
  }


if (workspaceMode === "home") {
  return (
    <ScienceTaskHome
      onQuickTranslation={openQuickTranslation}
      onProfessionalTranslation={openProfessionalTranslation}
      onOpenCurriculum={openCurriculum}
      onOpenQuestionBank={openQuestionBank}
      onOpenAssessmentBuilder={openAssessmentBuilder}
      onOpenDifferentiatedActivities={openDifferentiatedActivities}
      onOpenScientificDiagrams={openScientificDiagrams}
      onOpenCloudSources={openCloudSources}
    />
  );
}

if (workspaceMode === "cloud-sources") {
  return (
    <CloudSources
      projectId={projectId}
      onReturnHome={returnToTaskHome}
    />
  );
}

if (workspaceMode === "scientific-diagrams") {
  return (
    <ScientificDiagrams
      projectId={projectId}
      onReturnHome={returnToTaskHome}
    />
  );
}

if (workspaceMode === "differentiated-activities") {
  return (
    <DifferentiatedActivities
      projectId={projectId}
      onReturnHome={returnToTaskHome}
    />
  );
}

if (workspaceMode === "assessment") {
  return (
    <AssessmentBuilder
      projectId={projectId}
      onReturnHome={returnToTaskHome}
    />
  );
}

if (workspaceMode === "question-bank") {
  return (
    <QuestionBankLibrary
      projectId={projectId}
      onQuestionReused={(question) => {
        setQuestions((current) =>
          current.some((item) => item.id === question.id)
            ? current
            : [...current, question],
        );
        setLastSyncNote(
          "تمت إضافة سؤال من بنك الأسئلة إلى المشروع الحالي.",
        );
      }}
      onReturnHome={returnToTaskHome}
    />
  );
}

if (workspaceMode === "curriculum") {
  return (
    <CurriculumBrowser
      projectId={projectId}
      onReturnHome={returnToTaskHome}
    />
  );
}

if (workspaceMode === "quick") {
  return (
    <QuickTranslationWorkspace
      metadata={metadata}
      uploadedFile={uploadedFile}
      extractedText={extractedText}
      initialExtractionStatus={initialExtractionStatus}
      questions={questions}
      projectReadiness={projectReadiness}
      translationBatchSummary={translationBatchSummary}
      isBusy={apiStatus === "syncing" || apiStatus === "connecting"}
      apiStatus={apiStatus}
      lastSyncNote={lastSyncNote}
      quickRunStatus={quickRunStatus}
      quickRunMessage={quickRunMessage}
      onMetadataChange={handleMetadataChange}
      onFileSelected={handleFileSelected}
      onRetryInitialExtraction={retryInitialExtraction}
      onRunQuickTranslation={() => void runQuickTranslationWorkflow()}
      onOpenProfessionalReview={openQuickProfessionalReview}
      onOpenExport={openQuickExport}
      onReturnHome={returnToTaskHome}
    />
  );
}

  return (
    <WorkspaceShell
      sidebar={
        <WorkspaceSidebar
          steps={steps}
          activeIndex={activeIndex}
          onSelectStep={setActiveIndex}
          onOpenSettings={() => setAuthPanelOpen(true)}
        />
      }
      topbar={
        <WorkspaceTopBar
          metadata={metadata}
          apiStatus={apiStatus}
          lastSyncNote={lastSyncNote}
          projectId={projectId}
          onOpenStart={() => setActiveIndex(0)}
          onDownloadSnapshot={() => void downloadProjectSnapshot()}
          onImportSnapshot={(file) => void importProjectSnapshotFile(file)}
          onNewProject={() => void resetProject()}
        />
      }
      status={
        <WorkflowStatusStrip
          activeQuestions={approvedCount + needsReviewCount}
          needsReview={needsReviewCount}
          glossaryNeedsReview={glossary.filter((term) => term.status === "needs_review").length}
          outputLabel={metadata.outputMode === "bilingual" ? "ثنائي" : "عربي"}
        />
      }
    >
      <button
        type="button"
        className="workspace-task-home-button"
        onClick={returnToTaskHome}
      >
        العودة إلى المهام
      </button>
      <details
        className="workspace-settings-panel"
        open={isAuthPanelOpen}
        onToggle={(event) => setAuthPanelOpen(event.currentTarget.open)}
      >
        <summary className="workspace-settings-summary">
          <span>
            <strong>الحساب والصلاحيات</strong>
            <small>
              {authAccount
                ? `الحساب: ${authAccount.displayName}`
                : `الحساب غير مسجل · ${apiStatus === "offline" ? "وضع محلي" : "جاهز للربط"}`}
            </small>
          </span>
        </summary>
        <AuthPanel
          status={authStatus}
          account={authAccount}
          accounts={authAccounts}
          accountsLoading={authAccountsLoading}
          message={authMessage}
          onBootstrap={bootstrapOwnerAccount}
          onLogin={loginAccount}
          onLogout={logoutAccount}
          onRefreshAccounts={refreshAuthAccounts}
          onCreateAccount={createManagedAccount}
          onToggleAccount={toggleManagedAccount}
        />
      </details>

      <section className="workspace-stage-surface">
        <div className="step-header workspace-stage-header">
          <div>
            <p className="eyebrow">المرحلة {progressLabel}</p>
            <h2>{activeStep.label}</h2>
            <p>{activeStep.description}</p>
          </div>
          <DatabaseZap size={32} aria-hidden="true" />
        </div>

        <WorkspaceContent
          stageKey={activeStep.key}
          metadata={metadata}
          schoolLogo={schoolLogo}
          uploadedFile={uploadedFile}
          extractedText={extractedText}
          fullExamIntakeReport={fullExamIntakeReport}
          fullExamTranslationReport={fullExamTranslationReport}
          fullExamExportReport={fullExamExportReport}
          fullExamEndToEndReport={fullExamEndToEndReport}
          questions={questions}
          glossary={glossary}
          layoutAssets={layoutAssets}
          answerKey={answerKey}
          educationalAnalysis={educationalAnalysis}
          qualityTools={qualityTools}
          translationProviderStatus={translationProviderStatus}
          translationBatchSummary={translationBatchSummary}
          projectReadiness={projectReadiness}
          projects={projectLibrary}
          currentProjectId={projectId}
          isLibraryLoading={isProjectLibraryLoading}
          isBusy={apiStatus === "syncing" || apiStatus === "connecting"}
          initialExtractionStatus={initialExtractionStatus}
          lastSyncNote={lastSyncNote}
          onMetadataChange={handleMetadataChange}
          onLogoSelected={handleLogoSelected}
          onLogoRemove={handleLogoRemove}
          onFileSelected={handleFileSelected}
          onRetryInitialExtraction={retryInitialExtraction}
          onRefreshProjects={() => void refreshProjectLibrary()}
          onOpenProject={(id) => void openPersistedProject(id)}
          onDeleteProject={(id) => void deletePersistedProject(id)}
          onDeleteProjects={(ids) => void deletePersistedProjects(ids)}
          onUpdateQuestion={updateQuestion}
          onMoveQuestion={moveQuestion}
          onUpdateGlossaryTerm={updateGlossaryTerm}
          onGenerateGlossary={generateGlossaryFromQuestionCards}
          onApproveAllGlossary={approveAllCompletedGlossaryTerms}
          onTranslateQuestions={translateQuestions}
          onRetryQuestionTranslation={retryQuestionTranslationForReview}
          onBulkUpdateStatus={bulkUpdateReviewStatus}
          onUploadQuestionAsset={handleQuestionAssetUpload}
          onDeleteQuestionAsset={handleQuestionAssetDelete}
          onLinkQuestionLayoutAsset={handleQuestionLayoutAssetLink}
          onUnlinkQuestionLayoutAsset={handleQuestionLayoutAssetUnlink}
          onCropQuestionLayoutAsset={handleQuestionLayoutAssetCrop}
          onDeleteLayoutAsset={handleLayoutAssetDelete}
          onReloadDemo={reloadDemoFromBackend}
          onParseQuestions={parseQuestionsFromExtractedText}
          onExportDocx={exportDocx}
          onExportPdf={exportPdf}
          onRefreshReadiness={refreshProjectReadiness}
          onGenerateAnswerKey={generateProjectAnswerKey}
          onClearAnswerKey={clearProjectAnswerKey}
          onGenerateEducationalAnalysis={generateProjectEducationalAnalysis}
          onClearEducationalAnalysis={clearProjectEducationalAnalysis}
          onGenerateQualityTools={generateProjectQualityTools}
          onClearQualityTools={clearProjectQualityTools}
          onRunFullExamAcceptance={runFullExamAcceptanceGate}
          canExportDocx={Boolean(projectId && apiStatus !== "offline")}
          canExportPdf={Boolean(projectId && apiStatus !== "offline")}
        />

        <div className="actions-row workflow-actions-row workspace-stage-actions">
          <button
            className="secondary-button"
            type="button"
            onClick={goPrevious}
            disabled={activeIndex === 0}
          >
            <ArrowRight size={18} />
            السابق
          </button>
          {activeIndex < steps.length - 1 ? (
            <button
              className="primary-button"
              type="button"
              onClick={goNext}
              disabled={activeIndex === 0 && !canAdvanceFromStart}
            >
              {activeIndex === 0
                ? "الانتقال إلى المراجعة"
                : "الانتقال إلى التصدير"}
              <ArrowLeft size={18} />
            </button>
          ) : null}
          {activeIndex === 0 && !canAdvanceFromStart ? (
            <span className="workspace-next-requirement">
              أكمل رفع الملف واستخراج النص أولًا.
            </span>
          ) : null}
        </div>
      </section>
    </WorkspaceShell>
  );
}

interface WorkspaceContentProps {
  stageKey: WorkflowStageKey;
  metadata: ProjectMetadata;
  schoolLogo: SchoolLogoInfo | null;
  uploadedFile: UploadedFileInfo | null;
  extractedText: ExtractedTextInfo | null;
  fullExamIntakeReport: FullExamIntakeReport | null;
  fullExamTranslationReport: FullExamTranslationReport | null;
  fullExamExportReport: FullExamExportReport | null;
  fullExamEndToEndReport: FullExamEndToEndReport | null;
  questions: QuestionItem[];
  glossary: GlossaryTerm[];
  layoutAssets: PdfLayoutAssetInfo[];
  answerKey: AnswerKeyItem[];
  educationalAnalysis: EducationalAnalysisReport | null;
  qualityTools: EducationalQualityToolsReport | null;
  translationProviderStatus: TranslationProviderStatus | null;
  translationBatchSummary: TranslationBatchSummary | null;
  projectReadiness: ProjectReadinessReport | null;
  projects: ProjectSession[];
  currentProjectId: string | null;
  isLibraryLoading: boolean;
  isBusy: boolean;
  initialExtractionStatus: InitialExtractionStatus;
  lastSyncNote: string;
  onMetadataChange: (metadata: ProjectMetadata) => void;
  onLogoSelected: (file: File | null) => void;
  onLogoRemove: () => void;
  onFileSelected: (file: File | null) => void;
  onRetryInitialExtraction: () => void;
  onRefreshProjects: () => void;
  onOpenProject: (projectId: string) => void;
  onDeleteProject: (projectId: string) => void;
  onDeleteProjects: (projectIds: string[]) => void;
  onUpdateQuestion: (
    questionId: string,
    updates: Partial<QuestionItem>,
  ) => void;
  onMoveQuestion: (questionId: string, direction: "up" | "down") => void;
  onUpdateGlossaryTerm: (
    termId: string,
    updates: Partial<GlossaryTerm>,
  ) => void;
  onGenerateGlossary: () => void;
  onApproveAllGlossary: () => void;
  onTranslateQuestions: () => void;
  onRetryQuestionTranslation: (questionId: string) => void;
  onBulkUpdateStatus: (
    status: QuestionStatus,
    includeDeleted?: boolean,
  ) => void;
  onUploadQuestionAsset: (questionId: string, file: File) => void;
  onDeleteQuestionAsset: (questionId: string, assetId: string) => void;
  onLinkQuestionLayoutAsset: (questionId: string, assetId: string) => void;
  onUnlinkQuestionLayoutAsset: (questionId: string, assetId: string) => void;
  onCropQuestionLayoutAsset: (
    questionId: string,
    assetId: string,
    crop: VisualCropRequest,
  ) => Promise<void>;
  onDeleteLayoutAsset: (assetId: string) => void;
  onReloadDemo: () => void;
  onParseQuestions: () => void;
  onExportDocx: () => Promise<void>;
  onExportPdf: () => Promise<void>;
  onRefreshReadiness: () => Promise<void>;
  onGenerateAnswerKey: () => Promise<void>;
  onClearAnswerKey: () => Promise<void>;
  onGenerateEducationalAnalysis: () => Promise<void>;
  onClearEducationalAnalysis: () => Promise<void>;
  onGenerateQualityTools: () => Promise<void>;
  onClearQualityTools: () => Promise<void>;
  onRunFullExamAcceptance: () => Promise<void>;
  canExportDocx: boolean;
  canExportPdf: boolean;
}

function WorkspaceContent({
  stageKey,
  metadata,
  schoolLogo,
  uploadedFile,
  extractedText,
  fullExamIntakeReport,
  fullExamTranslationReport,
  fullExamExportReport,
  fullExamEndToEndReport,
  questions,
  glossary,
  layoutAssets,
  answerKey,
  educationalAnalysis,
  qualityTools,
  translationProviderStatus,
  translationBatchSummary,
  projectReadiness,
  projects,
  currentProjectId,
  isLibraryLoading,
  isBusy,
  initialExtractionStatus,
  lastSyncNote,
  onMetadataChange,
  onLogoSelected,
  onLogoRemove,
  onFileSelected,
  onRetryInitialExtraction,
  onRefreshProjects,
  onOpenProject,
  onDeleteProject,
  onDeleteProjects,
  onUpdateQuestion,
  onMoveQuestion,
  onUpdateGlossaryTerm,
  onGenerateGlossary,
  onApproveAllGlossary,
  onTranslateQuestions,
  onRetryQuestionTranslation,
  onBulkUpdateStatus,
  onUploadQuestionAsset,
  onDeleteQuestionAsset,
  onLinkQuestionLayoutAsset,
  onUnlinkQuestionLayoutAsset,
  onCropQuestionLayoutAsset,
  onDeleteLayoutAsset,
  onReloadDemo,
  onParseQuestions,
  onExportDocx,
  onExportPdf,
  onRefreshReadiness,
  onGenerateAnswerKey,
  onClearAnswerKey,
  onGenerateEducationalAnalysis,
  onClearEducationalAnalysis,
  onGenerateQualityTools,
  onClearQualityTools,
  onRunFullExamAcceptance,
  canExportDocx,
  canExportPdf,
}: WorkspaceContentProps) {
  if (stageKey === "start") {
    return (
      <StartWorkspace
        metadata={metadata}
        schoolLogo={schoolLogo}
        uploadedFile={uploadedFile}
        extractedText={extractedText}
        layoutAssets={layoutAssets}
        questions={questions}
        projects={projects}
        currentProjectId={currentProjectId}
        isLibraryLoading={isLibraryLoading}
        isBusy={isBusy}
        initialExtractionStatus={initialExtractionStatus}
        lastSyncNote={lastSyncNote}
        onMetadataChange={onMetadataChange}
        onLogoSelected={onLogoSelected}
        onLogoRemove={onLogoRemove}
        onFileSelected={onFileSelected}
        onRetryInitialExtraction={onRetryInitialExtraction}
        onRefreshProjects={onRefreshProjects}
        onOpenProject={onOpenProject}
        onDeleteProject={onDeleteProject}
        onDeleteProjects={onDeleteProjects}
        onParseQuestions={onParseQuestions}
      />
    );
  }

  if (stageKey === "review") {
    return (
      <UnifiedReviewWorkspace
        projectId={currentProjectId ?? ""}
        questions={questions}
        glossary={glossary}
        layoutAssets={layoutAssets}
        extractedText={extractedText}
        translationProviderStatus={translationProviderStatus}
        translationBatchSummary={translationBatchSummary}
        fullExamIntakeReport={fullExamIntakeReport}
        fullExamTranslationReport={fullExamTranslationReport}
        isBusy={isBusy}
        onUpdateQuestion={onUpdateQuestion}
        onMoveQuestion={onMoveQuestion}
        onTranslateQuestions={onTranslateQuestions}
        onRetryQuestionTranslation={onRetryQuestionTranslation}
        onBulkUpdateStatus={onBulkUpdateStatus}
        onUploadQuestionAsset={onUploadQuestionAsset}
        onDeleteQuestionAsset={onDeleteQuestionAsset}
        onLinkLayoutAsset={onLinkQuestionLayoutAsset}
        onUnlinkLayoutAsset={onUnlinkQuestionLayoutAsset}
        onCropLayoutAsset={onCropQuestionLayoutAsset}
        onUpdateGlossaryTerm={onUpdateGlossaryTerm}
        onGenerateGlossary={onGenerateGlossary}
        onApproveAllGlossary={onApproveAllGlossary}
        onDeleteLayoutAsset={onDeleteLayoutAsset}
        onReloadDemo={onReloadDemo}
        onParseQuestions={onParseQuestions}
      />
    );
  }

  return (
    <ExportStep
      metadata={metadata}
      schoolLogo={schoolLogo}
      questions={questions}
      glossary={glossary}
      answerKey={answerKey}
      educationalAnalysis={educationalAnalysis}
      qualityTools={qualityTools}
      readiness={projectReadiness}
      fullExamExportReport={fullExamExportReport}
      fullExamTranslationReport={fullExamTranslationReport}
      fullExamEndToEndReport={fullExamEndToEndReport}
      onRunFullExamAcceptance={onRunFullExamAcceptance}
      onMetadataChange={onMetadataChange}
      canExportDocx={canExportDocx}
      onExportDocx={onExportDocx}
      onExportPdf={onExportPdf}
      canExportPdf={canExportPdf}
      onRefreshReadiness={onRefreshReadiness}
      onGenerateAnswerKey={onGenerateAnswerKey}
      onClearAnswerKey={onClearAnswerKey}
      onGenerateEducationalAnalysis={onGenerateEducationalAnalysis}
      onClearEducationalAnalysis={onClearEducationalAnalysis}
      onGenerateQualityTools={onGenerateQualityTools}
      onClearQualityTools={onClearQualityTools}
    />
  );
}
