"""Fetch the 10 hottest posts from a subreddit.

Example output (r/brdev):

     1. [   63] [Moderação] Sobre temas recorrentes e conteúdo de baixo esforço
          by u/AutoModerator — 13 comments
          https://www.reddit.com/r/brdev/comments/1rgamvt/...

     2. [   15] [Moderação] Oferecer ou compartilhar orientações médicas
          by u/AutoModerator — 0 comments
          https://www.reddit.com/r/brdev/comments/1ojjhti/...

     3. [   48] Criei um servidor MCP open-source para o LinkedIn
          by u/Consistent-Arm-3878 — 7 comments
          https://www.reddit.com/r/brdev/comments/1ro85d4/...

     4. [    8] Criei uma alternativa Open Source ao Codex App pra você codar usando IA
          by u/wygor96 — 0 comments
          https://www.reddit.com/r/brdev/comments/1rokshz/...

     5. [   83] Fuçando minhas coisas, encontrei um código de 600 linhas em Portugol
          by u/Dramatic-Revenue-802 — 7 comments
          https://www.reddit.com/r/brdev/comments/1ro269a/...

     6. [   91] Qual o plano B de vocês caso a área piore muito?
          by u/Spiritual_Pangolin18 — 185 comments
          https://www.reddit.com/r/brdev/comments/1rnytuh/...

     7. [   11] Como se vender, principalmente em entrevistas?
          by u/redfaf — 13 comments
          https://www.reddit.com/r/brdev/comments/1rocoba/...

     8. [   10] Alguém aqui usando spec-driven development com IA?
          by u/StatusPhilosopher258 — 13 comments
          https://www.reddit.com/r/brdev/comments/1ro9n82/...

     9. [    7] Processo seletivo Nubank
          by u/MonsteraV — 32 comments
          https://www.reddit.com/r/brdev/comments/1ro9z2d/...

    10. [    2] Ajuda com orientação de carreira, dev rn com "3,5 anos de exp"
          by u/Zealousideal-Care643 — 5 comments
          https://www.reddit.com/r/brdev/comments/1roip12/...
"""

from redd import Category, Redd

with Redd() as r:
    posts = r.get_subreddit_posts("brdev", limit=10, category=Category.HOT)

    for i, post in enumerate(posts, 1):
        print(f"{i:>2}. [{post.score:>5}] {post.title}")
        print(f"     by u/{post.author} — {post.num_comments} comments")
        print(f"     {post.url}")
        print()
