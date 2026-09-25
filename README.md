# 🎬 EYXO | KA Compressor (GIF)

**Compressão inteligente de GIFs animados com alvo exato de KB**

---

## O que faz

- Comprime arquivos GIF garantindo que não ultrapassem o limite exato de peso especificado (ex: 200KB).
- Utiliza um algoritmo de **Busca Binária** avançada para encontrar o equilíbrio perfeito entre compressão e a maior fidelidade visual possível para cada arquivo.
- Processa múltiplos GIFs simultaneamente em lote (batch processing).
- Organiza a saída, permitindo o download individual de cada arquivo otimizado ou um pacote consolidado (`.zip`).

## Como instalar

1. Instale o manipulador de GIFs abrindo o terminal do seu Mac e rodando: 
   `brew install gifsicle`
2. Instale as dependências da aplicação rodando: 
   `pip install flask werkzeug numpy`
3. O aplicativo já estará pronto para uso!

## Como usar

1. Na pasta do projeto, dê um duplo clique no arquivo **`Iniciar_Servidor.command`**. Ele irá ligar o servidor local e abrir a interface no seu navegador automaticamente.
2. Arraste seus GIFs para a área de upload ou clique para procurá-los.
3. Ajuste o peso máximo desejado (KB) para cada GIF ou aplique um limite único para todos usando o campo no topo da lista.
4. Clique em **COMPRIMIR** para iniciar o processo.
5. Após a conclusão, clique em **BAIXAR ZIP** para salvar todas as mídias prontas.

---

## Tecnologia

- **Motor de Compressão:** Executa o poderoso `gifsicle` por baixo dos panos, iterado através de uma lógica customizada de **Busca Binária (Binary Search)** escrita em Python. O algoritmo ajusta dinamicamente a agressividade do `lossy` e a redução do colormap para encontrar com precisão matemática a melhor qualidade dentro da restrição imposta pelo usuário.
- **Backend/Frontend:** Servidor ultraleve em Flask (Python) com interface frontend limpa em Vanilla JS e CSS, suportando feedback assíncrono em tempo real durante a compressão sem travar a navegação.
- **Segurança:** A ferramenta opera 100% de forma local (`localhost`). Nenhuma imagem é transferida pela internet, preservando totalmente a segurança e sigilo dos ativos.

---

## Suporte

Encontrou algum bug, erro bizarro na imagem ou o app recusou iniciar? 
Me chame no Discord: **`leomaia.eyxo`**

---

## Histórico (Changelog)

- **v2.8.9** - Manutenção: Atualizações gerais e adequações finais na renderização dos painéis.
- **v2.8.8** - UI Design System: Ajuste visual do feedback em tempo real para respeitar o Design System.
