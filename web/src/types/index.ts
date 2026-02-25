// Shared domain types

export type Plan = 'starter' | 'pro' | 'enterprise';

export interface LicenseInfo {
  valid: boolean;
  plan: Plan;
  email?: string;
  active?: boolean;
}

export interface AgentTask {
  id: string;
  name: string;
  task: string;
  active: boolean;
  created_at?: number;
}

export interface TestResult {
  taskId: string;
  widgets: WidgetResponse[];
  error?: string;
}

export interface WidgetParams {
  title?: string;
  subtitle?: string;
  text?: string;
  description?: string;
  message?: string;
  content?: string;
  emoji?: string;
  image_url?: string;
  button_text?: string;
  action_text?: string;
  badge_text?: string;
  question?: string;
  options?: (string | { label?: string; text?: string })[];
  max_stars?: number;
  progress?: number;
  progress_label?: string;
  [key: string]: unknown;
}

export interface WidgetCommon {
  priority?: number;
  [key: string]: unknown;
}

export interface WidgetResponse {
  id?: string;
  type: string;
  params: WidgetParams;
  common?: WidgetCommon;
}

export interface SuggestWidgetResponse {
  widgets: WidgetResponse[];
  [key: string]: unknown;
}

export interface AdminStats {
  total_licenses: number;
  active_licenses: number;
  by_plan?: Partial<Record<Plan, number>>;
  [key: string]: unknown;
}

export interface AdminLicense {
  api_key_masked: string;
  plan: Plan;
  email?: string;
  active: boolean;
  created_at?: number;
}

export interface PaddleConfig {
  env: string;
  publishableToken: string;
  priceIds: Record<string, string>;
}

export interface CheckoutResult {
  status: 'completed' | 'closed';
  data?: unknown;
}
