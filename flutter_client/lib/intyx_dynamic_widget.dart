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
    'title_subtitle_image': (p) => TitleSubtitleImageCard.fromJson(p),
    'clickable_image_link': (p) => ClickableImageLinkCard.fromJson(p),
    'hero_image': (p) => HeroImageCard.fromJson(p),
    'icon_text_action': (p) => IconTextActionCard.fromJson(p),
    'countdown_banner': (p) => CountdownBannerCard.fromJson(p),
    'carousel': (p) => CarouselCard.fromJson(p),
    'promotional': (p) => PromotionalWidget.fromJson(p),
    'contextual': (p) => ContextualWidget.fromJson(p),
    'informational': (p) => InformationalWidget.fromJson(p),
    'functional': (p) => FunctionalWidget.fromJson(p),
    'rating': (p) => RatingCard.fromJson(p),
    'poll': (p) => PollCard.fromJson(p),
    'social_proof': (p) => SocialProofCard.fromJson(p),
    'progress': (p) => ProgressCard.fromJson(p),
    'profile': (p) => ProfileCard.fromJson(p),
    'banner': (p) => BannerCard.fromJson(p),
  });
}
