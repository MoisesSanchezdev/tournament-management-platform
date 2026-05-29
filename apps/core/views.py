from django.shortcuts import render

from apps.participants.models import SchoolRegistration, UniversityRegistration
from apps.tournament.models import RuleSection, TournamentEdition


def sponsor_catalog():
    sponsors = [
        {
            "name": "Universidad Tecnologica de Pereira",
            "short_name": "UTP",
            "tagline": "Institucion anfitriona del torneo",
            "url": "https://www.utp.edu.co/",
            "logo_path": "sponsors/utp.png",
            "accent": "#67ecff",
            "accent_soft": "#173f7f",
            "link_ready": True,
        },
        {
            "name": "Ingenieria Electronica UTP",
            "short_name": "IE UTP",
            "tagline": "Programa organizador",
            "url": "https://ingenierias.utp.edu.co/ingenieria-electronica/",
            "logo_path": "sponsors/ingenieria-electronica-utp.png",
            "accent": "#2f7eff",
            "accent_soft": "#102d67",
            "link_ready": True,
        },
        {
            "name": "ASE UTP",
            "short_name": "ASE",
            "tagline": "Asociacion de Egresados UTP",
            "url": "https://egresados.utp.edu.co/page-asociacion-egresados/",
            "logo_path": "sponsors/ase-utp.png",
            "accent": "#ffc940",
            "accent_soft": "#6a4c06",
            "link_ready": True,
        },
        {
            "name": "Integra S.A.",
            "short_name": "INTEGRA",
            "tagline": "Operador de transporte masivo",
            "url": "http://www.integra.com.co",
            "logo_path": "sponsors/integra.png",
            "accent": "#53bdf3",
            "accent_soft": "#10486b",
            "link_ready": True,
        },
        {
            "name": "Energia de Pereira",
            "short_name": "EEP",
            "tagline": "Empresa de Energia de Pereira",
            "url": "https://www.eep.com.co/",
            "logo_path": "sponsors/energia-de-pereira.png",
            "accent": "#ff9b32",
            "accent_soft": "#66360b",
            "link_ready": True,
        },
        {
            "name": "Impointer",
            "short_name": "IMPOINTER",
            "tagline": "Soluciones didacticas e industriales",
            "url": "https://www.impointer.com/",
            "logo_path": "sponsors/impointer.png",
            "accent": "#35d3ad",
            "accent_soft": "#0a5749",
            "link_ready": True,
        },
        {
            "name": "Mutual Ingenieria",
            "short_name": "MUTUAL",
            "tagline": "Aliado empresarial del torneo",
            "url": None,
            "logo_path": "sponsors/mutual-ingenieria.png",
            "accent": "#4d6dff",
            "accent_soft": "#16245f",
            "link_ready": False,
        },
        {
            "name": "INGE LEAN S.A.S",
            "short_name": "INGE LEAN",
            "tagline": "Ingenieria especializada a la medida",
            "url": "https://www.ingelean.com/",
            "logo_path": "sponsors/inge-lean.png",
            "accent": "#ffb47c",
            "accent_soft": "#663716",
            "link_ready": True,
        },
        {
            "name": "Ideas varita magica",
            "short_name": "VARITA",
            "tagline": "Emprendimiento aliado",
            "url": None,
            "logo_path": "sponsors/ideas-varita-magica.png",
            "accent": "#f7f4ef",
            "accent_soft": "#49413a",
            "link_ready": False,
        },
        {
            "name": "NARA Sistem Online",
            "short_name": "NARA",
            "tagline": "Aliado digital",
            "url": None,
            "logo_path": "sponsors/nara-sistem-online.png",
            "accent": "#5aa2ff",
            "accent_soft": "#173d7b",
            "link_ready": False,
        },
    ]
    return sponsors


def home(request):
    edition = TournamentEdition.objects.filter(is_active=True).order_by("-start_date").first()
    rules = RuleSection.objects.filter(is_published=True).order_by("order", "title")[:6]
    school_total = SchoolRegistration.objects.filter(edition=edition).count() if edition else 0
    university_total = UniversityRegistration.objects.filter(edition=edition).count() if edition else 0
    sponsors = sponsor_catalog()
    showcase_images = [
        {
            "url": "https://comunicaciones.utp.edu.co/wp-content/uploads/sites/2/Portada-29-2-edited-scaled.jpg",
            "title": "Encuentro de robots y comunidad UTP",
            "caption": "Memoria visual del ambiente academico y competitivo alrededor de Ingenieria Electronica UTP.",
        },
        {
            "url": "https://comunicaciones.utp.edu.co/wp-content/uploads/sites/2/IMG_2608-1-1024x788.jpg",
            "title": "Semana de Ingenieria Electronica",
            "caption": "Espacios de innovacion, muestras y actividades que conectan estudiantes, docentes y tecnologia.",
        },
        {
            "url": "https://comunicaciones.utp.edu.co/wp-content/uploads/sites/2/IMG_2599-1024x748.jpg",
            "title": "Comunidad y experiencias del programa",
            "caption": "Una referencia visual para mostrar que el torneo hace parte de una cultura viva dentro del programa.",
        },
    ]
    context = {
        "edition": edition,
        "rules": rules,
        "school_total": school_total,
        "university_total": university_total,
        "showcase_images": showcase_images,
        "sponsors_preview": sponsors[:6],
        "sponsors_total": len(sponsors),
    }
    return render(request, "core/home.html", context)


def rules_page(request):
    edition = TournamentEdition.objects.filter(is_active=True).order_by("-start_date").first()
    rules = RuleSection.objects.filter(is_published=True).order_by("order", "title")
    return render(request, "core/rules.html", {"edition": edition, "rules": rules})


def sponsors_page(request):
    edition = TournamentEdition.objects.filter(is_active=True).order_by("-start_date").first()
    sponsors = sponsor_catalog()
    ready_count = sum(1 for sponsor in sponsors if sponsor["link_ready"])
    return render(
        request,
        "core/sponsors.html",
        {
            "edition": edition,
            "sponsors": sponsors,
            "ready_count": ready_count,
        },
    )
