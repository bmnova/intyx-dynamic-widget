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

export interface ColorPalette {
  primary?: string;
  primary_variant?: string;
  secondary?: string;
  secondary_variant?: string;
  background?: string;
  surface?: string;
  error?: string;
  on_primary?: string;
  on_secondary?: string;
  on_background?: string;
  on_surface?: string;
  on_error?: string;
  border_radius?: number;
  elevation?: number;
}

export interface CarouselItem {
  title?: string;
  description?: string;
  image_url?: string;
  image_fit?: string;
  link_url?: string;
  style?: string;
}

export interface WidgetAction {
  label?: string;
  action?: string;
  url?: string;
  style?: string;
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
  image_fit?: string;
  button_text?: string;
  button_action?: string;
  action_text?: string;
  action_url?: string;
  badge_text?: string;
  question?: string;
  options?: (string | { label?: string; text?: string })[];
  max_stars?: number;
  progress?: number;
  progress_label?: string;
  end_time?: string;
  icon?: string;
  source?: string;
  severity?: string;
  link_url?: string;
  link_text?: string;
  metric?: string | number;
  metric_label?: string;
  testimonial?: string;
  quote?: string;
  author_name?: string;
  author?: string;
  author_title?: string;
  avatar_url?: string;
  name?: string;
  items?: CarouselItem[];
  actions?: WidgetAction[];
  style?: string;
  [key: string]: unknown;
}

export interface WidgetCommon {
  priority?: number;
  dismissible?: boolean;
  ttl_seconds?: number | null;
  color_palette?: ColorPalette;
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

export interface UsageCounter {
  used: number;
  limit: number;
  percent?: number;
}

export interface UsageStats {
  plan: Plan;
  api_calls: UsageCounter;
  mau: UsageCounter;
  resets_at: string;
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
