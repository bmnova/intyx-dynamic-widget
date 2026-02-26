/// Intyx Dynamic Widget System
///
/// AI-driven, JSON-configured, responsive widget package for Flutter.
/// Widgets are determined by an AI agent and rendered dynamically
/// based on JSON responses.
library intyx_dynamic_widget;

// Core
export 'core/catalog_provider.dart';
export 'core/intyx_init.dart';
export 'core/responsive_widget_wrapper.dart';
export 'core/widget_registry.dart';
export 'core/widget_resolver.dart';

// Models
export 'models/trigger_context.dart';
export 'models/widget_definition.dart';
export 'models/widget_response.dart';

// Services
export 'services/firebase_service.dart';
export 'services/widget_service.dart';

// Widgets - Dynamic/Trigger
export 'widgets/contextual_widget.dart';
export 'widgets/dynamic_widget_container.dart';
export 'widgets/functional_widget.dart';
export 'widgets/informational_widget.dart';
export 'widgets/promotional_widget.dart';

// Widgets - UI Cards
export 'widgets/ui/banner_card.dart';
export 'widgets/ui/carousel_card.dart';
export 'widgets/ui/clickable_image_link_card.dart';
export 'widgets/ui/countdown_banner_card.dart';
export 'widgets/ui/hero_image_card.dart';
export 'widgets/ui/icon_text_action_card.dart';
export 'widgets/ui/poll_card.dart';
export 'widgets/ui/profile_card.dart';
export 'widgets/ui/progress_card.dart';
export 'widgets/ui/rating_card.dart';
export 'widgets/ui/social_proof_card.dart';
export 'widgets/ui/title_subtitle_image_card.dart';

// --- Default Registration ---

import 'core/widget_registry.dart';
import 'widgets/contextual_widget.dart';
import 'widgets/functional_widget.dart';
import 'widgets/informational_widget.dart';
import 'widgets/promotional_widget.dart';
import 'widgets/ui/banner_card.dart';
import 'widgets/ui/carousel_card.dart';
import 'widgets/ui/clickable_image_link_card.dart';
import 'widgets/ui/countdown_banner_card.dart';
import 'widgets/ui/hero_image_card.dart';
import 'widgets/ui/icon_text_action_card.dart';
import 'widgets/ui/poll_card.dart';
import 'widgets/ui/profile_card.dart';
import 'widgets/ui/progress_card.dart';
import 'widgets/ui/rating_card.dart';
import 'widgets/ui/social_proof_card.dart';
import 'widgets/ui/title_subtitle_image_card.dart';

/// Call this once at app startup to register all built-in widget types.
void registerDefaultWidgets() {
  WidgetRegistry.registerAll({
    'title_subtitle_image': (p, {onAction}) => TitleSubtitleImageCard.fromJson(p, onAction: onAction),
    'clickable_image_link': (p, {onAction}) => ClickableImageLinkCard.fromJson(p, onAction: onAction),
    'hero_image': (p, {onAction}) => HeroImageCard.fromJson(p, onAction: onAction),
    'icon_text_action': (p, {onAction}) => IconTextActionCard.fromJson(p, onAction: onAction),
    'countdown_banner': (p, {onAction}) => CountdownBannerCard.fromJson(p),
    'carousel': (p, {onAction}) => CarouselCard.fromJson(p),
    'promotional': (p, {onAction}) => PromotionalWidget.fromJson(p, onAction: onAction),
    'contextual': (p, {onAction}) => ContextualWidget.fromJson(p, onAction: onAction),
    'informational': (p, {onAction}) => InformationalWidget.fromJson(p, onAction: onAction),
    'functional': (p, {onAction}) => FunctionalWidget.fromJson(p, onAction: onAction),
    'rating': (p, {onAction}) => RatingCard.fromJson(p),
    'poll': (p, {onAction}) => PollCard.fromJson(p),
    'social_proof': (p, {onAction}) => SocialProofCard.fromJson(p),
    'progress': (p, {onAction}) => ProgressCard.fromJson(p),
    'profile': (p, {onAction}) => ProfileCard.fromJson(p),
    'banner': (p, {onAction}) => BannerCard.fromJson(p, onAction: onAction),
  });
}
