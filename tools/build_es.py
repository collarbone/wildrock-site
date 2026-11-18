#!/usr/bin/env python3
"""Generate es/index.html from index.html.

index.html is the single source for layout and styles; this script swaps in the
Spanish copy below. Every English string must be found, so if the English copy
changes the build fails and names the string whose translation needs updating.

Usage: python3 tools/build_es.py
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

# (english, spanish) pairs, applied in order. Each English string must appear at least once;
# every occurrence is replaced. Include surrounding markup where a word alone would be ambiguous.
PAIRS = [
    # page-level
    ('<html lang="en">', '<html lang="es">'),
    ('<title>Wildrock — Spec Homes &amp; Small Multifamily in Northwest Arkansas</title>',
     '<title>Wildrock — Casas nuevas y vivienda multifamiliar en el noroeste de Arkansas</title>'),
    ('<meta property="og:title" content="Wildrock — Spec Homes &amp; Small Multifamily in Northwest Arkansas">',
     '<meta property="og:title" content="Wildrock — Casas nuevas y vivienda multifamiliar en el noroeste de Arkansas">'),
    ('content="Wildrock designs and builds spec homes and small to mid-size apartment buildings in Northwest Arkansas — well-designed, attainably priced places shaped around how people actually live."',
     'content="Wildrock diseña y construye casas nuevas para la venta y edificios de apartamentos pequeños y medianos en el noroeste de Arkansas: lugares bien diseñados, a precios accesibles, pensados en cómo vive la gente."'),
    ('content="Designing your home is designing your life. Well-made spec homes and small multifamily, shaped around how people live."',
     'content="Diseñar su hogar es diseñar su vida. Casas nuevas y vivienda multifamiliar bien hechas, pensadas en cómo vive la gente."'),
    ('<link rel="canonical" href="https://wildrock.build/">', '<link rel="canonical" href="https://wildrock.build/es/">'),
    ('<meta property="og:url" content="https://wildrock.build/">', '<meta property="og:url" content="https://wildrock.build/es/">'),
    ('<meta property="og:locale" content="en_US">\n<meta property="og:locale:alternate" content="es_US">',
     '<meta property="og:locale" content="es_US">\n<meta property="og:locale:alternate" content="en_US">'),
    ('src="images/', 'src="../images/'),

    # header
    ('>Skip to content<', '>Saltar al contenido<'),
    ('aria-label="Wildrock — back to top"', 'aria-label="Wildrock — volver al inicio"'),
    ('aria-controls="site-nav">Menu</button>', 'aria-controls="site-nav">Menú</button>'),
    ("open ? 'Close' : 'Menu'", "open ? 'Cerrar' : 'Menú'"),
    ('aria-label="Primary"', 'aria-label="Principal"'),
    ('<a href="#approach">Approach</a>', '<a href="#approach">Enfoque</a>'),
    ('<a href="#build">What we build</a>', '<a href="#build">Qué construimos</a>'),
    ('<a href="#trades">Trades &amp; partners</a>', '<a href="#trades">Contratistas y socios</a>'),
    ('<a class="contact-link" href="#contact">Contact</a>', '<a class="contact-link" href="#contact">Contacto</a>'),
    ('data-lang="en" aria-current="true">EN</a>', 'data-lang="en">EN</a>'),
    ('data-lang="es">ES</a>', 'data-lang="es" aria-current="true">ES</a>'),

    # hero
    ('Designing your home is designing your life.</h1>', 'Diseñar su hogar es diseñar su vida.</h1>'),
    ('<p>We specialize in designing &amp; building spec homes and small multifamily in Northwest Arkansas.</p>',
     '<p>Nos especializamos en diseñar y construir casas nuevas para la venta y vivienda multifamiliar en el noroeste de Arkansas.</p>'),
    ('>Get in touch <span', '>Contáctenos <span'),
    ('<li>Residential design &amp; construction</li>', '<li>Diseño y construcción residencial</li>'),
    ('<li>Spec homes</li>', '<li>Casas para la venta</li>'),
    ('<li>Duplex to mid-size multifamily</li>', '<li>De dúplex a multifamiliar mediana</li>'),
    ('<li>Owner-led</li>', '<li>Dirigida por su dueño</li>'),
    ('alt="A new timber-framed home rising on an open lot at dusk, with fields and tree lines beyond"',
     'alt="Una casa nueva con estructura de madera levantándose en un terreno abierto al atardecer, con campos y arboledas al fondo"'),

    # 01 approach
    ('</span>Approach</p><p class="eyebrow">What we believe</p>', '</span>Enfoque</p><p class="eyebrow">Lo que creemos</p>'),
    ('>Well-made places, shaped around how people live, at prices they can reach.</p>',
     '>Lugares bien hechos, pensados en cómo vive la gente, a precios a su alcance.</p>'),
    ('alt="Late light falling through tall windows across a quiet living room"',
     'alt="Luz de la tarde entrando por ventanas altas en una sala tranquila"'),
    ('>A home shapes the life inside it.</h2>', '>Un hogar da forma a la vida que hay dentro.</h2>'),
    ('>Light in the morning, a kitchen people gather in, storage where it is needed, a quiet room to think. We design every project around the everyday lives of the people who will call it home, then build it to last, without pricing it out of reach.</p>',
     '>Luz por la mañana, una cocina donde la familia se reúne, espacio para guardar donde hace falta, un cuarto tranquilo para pensar. Diseñamos cada proyecto en torno a la vida diaria de quienes lo llamarán hogar, y lo construimos para que dure, sin que su precio quede fuera de alcance.</p>'),
    ('>Designed for daily life</h3><p>Plans that start with how people actually live: flow, light, privacy and room to grow.</p>',
     '>Diseñado para la vida diaria</h3><p>Planos que parten de cómo vive realmente la gente: circulación, luz, privacidad y espacio para crecer.</p>'),
    ('>Built to last</h3><p>Honest, durable materials and careful detailing that hold up long after the sale.</p>',
     '>Construido para durar</h3><p>Materiales honestos y duraderos, y detalles cuidados que resisten mucho después de la venta.</p>'),
    ('>Priced within reach</h3><p>Disciplined design and efficient building, so good homes stay attainable.</p>',
     '>Precios a su alcance</h3><p>Diseño disciplinado y construcción eficiente, para que las buenas casas sigan siendo accesibles.</p>'),

    # 02 what we build
    ('</span>What we build</p><p class="eyebrow">Projects</p>', '</span>Qué construimos</p><p class="eyebrow">Proyectos</p>'),
    ('>Bespoke projects, designed and built in-house.</h2>', '>Proyectos a la medida, diseñados y construidos por nosotros.</h2>'),
    ('alt="Open floor framed in timber, with layout marks on the subfloor"',
     'alt="Piso abierto con estructura de madera y marcas de trazado sobre el contrapiso"'),
    ('>Spec homes</h3><p>Our primary focus. Single-family homes we develop, design and build ourselves, each one a considered original, not a copy from a catalog.</p>',
     '>Casas para la venta</h3><p>Nuestro enfoque principal. Casas unifamiliares que desarrollamos, diseñamos y construimos nosotros mismos, cada una un original pensado con cuidado, no una copia de catálogo.</p>'),
    ('>Small multifamily</h3><p>Duplexes, townhomes and small to mid-size apartment buildings, held to the same standard of design as our homes.</p>',
     '>Multifamiliar pequeña</h3><p>Dúplex, casas adosadas y edificios de apartamentos pequeños y medianos, con el mismo nivel de diseño que nuestras casas.</p>'),
    ('>Design-build</h3><p>Design and construction under one roof, from land and plans through to final inspection.</p>',
     '>Diseño y construcción</h3><p>Diseño y construcción bajo un mismo techo, desde el terreno y los planos hasta la inspección final.</p>'),

    # 03 trades & partners
    ('</span>Trades &amp; partners</p><p class="eyebrow">Build with us</p>', '</span>Contratistas y socios</p><p class="eyebrow">Construya con nosotros</p>'),
    ('>Good buildings take good people.</h2>', '>Los buenos edificios requieren buena gente.</h2>'),
    ('>We work with subcontractors, suppliers, architects and land partners who take pride in their work. If that is you, we would like to hear from you.</p>',
     '>Trabajamos con subcontratistas, proveedores, arquitectos y socios de terrenos que se enorgullecen de su trabajo. Si ese es su caso, nos gustaría saber de usted.</p>'),
    ('data-subject="Trade / partner introduction">Introduce yourself <span',
     'data-subject="Presentación de contratista / socio">Preséntese <span'),
    ('<li>Complete plans and clear scopes before work starts</li>', '<li>Planos completos y alcances claros antes de empezar</li>'),
    ('<li>Organized schedules and a ready site</li>', '<li>Calendarios organizados y una obra lista</li>'),
    ('<li>Direct, owner-level communication</li>', '<li>Comunicación directa con el dueño</li>'),
    ('<li>Fair, on-time payment</li>', '<li>Pagos justos y a tiempo</li>'),

    # 04 contact
    ("</span>Contact</p><p class=\"eyebrow\">Let's talk</p>", '</span>Contacto</p><p class="eyebrow">Hablemos</p>'),
    (">Let's build something worth living in.</h2>", '>Construyamos algo en lo que valga la pena vivir.</h2>'),
    ('>For trades, partners, land and project enquiries, email is the best way to reach us.</p>',
     '>Para contratistas, socios, terrenos y consultas sobre proyectos, el correo electrónico es la mejor forma de comunicarse con nosotros.</p>'),
    ('>Email Wildrock <span', '>Escribir a Wildrock <span'),
    ('<dt>Email</dt>', '<dt>Correo electrónico</dt>'),
    ('jamison [at] wildrock [dot] build', 'jamison [arroba] wildrock [punto] build'),
    ('<dt>Based in</dt>', '<dt>Ubicación</dt>'),
    ('<dt>Focus</dt><dd>Spec homes &amp; small multifamily</dd>', '<dt>Especialidad</dt><dd>Casas para la venta y vivienda multifamiliar</dd>'),

    # footer
    ('&copy; 2026 Wildrock. All rights reserved.', '&copy; 2026 Wildrock. Todos los derechos reservados.'),

    # shared short strings last, after the longer sentences containing them are done
    ('Northwest Arkansas<', 'Noroeste de Arkansas<'),
]


def main():
    src = (ROOT / 'index.html').read_text()

    out = src

    missing = []
    for en, es in PAIRS:
        if en not in out:
            missing.append(en)
        out = out.replace(en, es)
    if missing:
        print('build_es: these English strings were not found in index.html.\n'
              'The English copy probably changed; update PAIRS in tools/build_es.py:\n', file=sys.stderr)
        for m in missing:
            print('  - ' + m[:140], file=sys.stderr)
        sys.exit(1)

    dest = ROOT / 'es' / 'index.html'
    dest.parent.mkdir(exist_ok=True)
    dest.write_text(out)
    print(f'wrote {dest.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
