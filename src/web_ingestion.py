import requests
from bs4 import BeautifulSoup
import re

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings


# 🔹 Load already processed URLs
processed_urls = set()
try:
    with open("processed_urls.txt", "r") as f:
        processed_urls = set(f.read().splitlines())
except:
    pass


# 🔥 NEW: extract title from URL (Perplexity-style)
def extract_title(url):
    match = re.search(r'(?:https?://)?(?:www\.)?([^/]+)', url)
    if match:
        name = match.group(1).split('.')[0]
        return name.capitalize()
    return "Source"


def scrape_text(url):
    print(f"🌐 Scraping: {url}")

    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        paragraphs = soup.find_all("p")
        text = "\n".join([p.get_text() for p in paragraphs])

        return text

    except Exception as e:
        print(f"❌ Failed to scrape {url}: {e}")
        return ""


def ingest_web(urls):
    print("🚀 Starting web ingestion...\n")

    docs = []
    new_urls = []

    for url in urls:
        if url in processed_urls:
            print(f"⏩ Skipping already processed: {url}")
            continue

        text = scrape_text(url)

        # Skip low-content pages
        if len(text.strip()) < 200:
            continue

        docs.append({
            "content": text,
            "source": url,
            "title": extract_title(url)  # 🔥 ADDED
        })

        new_urls.append(url)

    print(f"📄 Scraped {len(docs)} new pages")

    if len(docs) == 0:
        print("⚠️ No new content to process")
        return

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )

    chunks = []
    for doc in docs:
        split = splitter.split_text(doc["content"])

        for chunk in split:
            chunks.append({
                "page_content": chunk,
                "metadata": {
                    "source": doc["source"],
                    "title": doc["title"]   # 🔥 ADDED
                }
            })

    print(f"🔹 Created {len(chunks)} chunks")

    # ⚡ Limit chunks for performance
    chunks = chunks[:300]

    print(f"⚡ Using {len(chunks)} chunks (limited for speed)")

    embeddings = OllamaEmbeddings(model="nomic-embed-text")

    db = Chroma(
        persist_directory="db",
        embedding_function=embeddings
    )

    db.add_texts(
        texts=[c["page_content"] for c in chunks],
        metadatas=[c["metadata"] for c in chunks]
    )

    # 🔹 Save processed URLs
    with open("processed_urls.txt", "a") as f:
        for url in new_urls:
            f.write(url + "\n")

    print("✅ Web ingestion complete!")


if __name__ == "__main__":
    urls = [
        "https://www.geeksforgeeks.org/system-design/system-design-tutorial/",
        "https://bytebytego.com/courses/system-design-interview/scale-from-zero-to-millions-of-users",
        "https://github.com/donnemartin/system-design-primer",
        "https://www.systemdesignhandbook.com/guides/system-design/",
        "https://github.com/karanpratapsingh/system-design",
        "https://www.geeksforgeeks.org/system-design/getting-started-with-system-design/",
        "https://www.geeksforgeeks.org/software-engineering/functional-vs-non-functional-requirements/",
        "https://www.geeksforgeeks.org/system-design/difference-between-high-level-design-and-low-level-design/",
        "https://www.geeksforgeeks.org/system-design/what-is-high-level-design-learn-system-design/",
        "https://www.geeksforgeeks.org/system-design/how-to-draw-high-level-design-diagram/",
        "https://www.geeksforgeeks.org/system-design/monolithic-architecture-system-design/",
        "https://www.geeksforgeeks.org/system-design/microservices/",
        "https://www.geeksforgeeks.org/software-engineering/monolithic-vs-microservices-architecture/",
        "https://www.geeksforgeeks.org/system-design/event-driven-architecture-system-design/",
        "https://www.geeksforgeeks.org/system-design/serverless-architectures/",
        "https://www.geeksforgeeks.org/system-design/stateful-vs-stateless-architecture/",
        "https://www.geeksforgeeks.org/system-design/what-is-pub-sub/",
        "https://www.geeksforgeeks.org/system-design/what-is-scalability/",
        "https://www.geeksforgeeks.org/system-design/system-design-horizontal-and-vertical-scaling/",
        "https://www.geeksforgeeks.org/system-design/which-scalability-approach-is-right-for-our-application-system-design/",
        "https://www.geeksforgeeks.org/system-design/guide-for-designing-highly-scalable-systems/",
        "https://www.geeksforgeeks.org/system-design/primary-bottlenecks-that-hurt-the-scalability-of-an-application-system-design/",
        "https://www.geeksforgeeks.org/system-design/complete-reference-to-databases-in-designing-systems/",
        "https://www.geeksforgeeks.org/system-design/types-of-databases-in-system-design/",
        "https://www.geeksforgeeks.org/system-design/which-database-to-choose-while-designing-a-system-sql-or-nosql/",
        "https://www.geeksforgeeks.org/system-design/file-and-database-storage-systems-in-system-design/",
        "https://www.geeksforgeeks.org/system-design/database-replication-and-their-types-in-system-design/",
        "https://www.geeksforgeeks.org/system-design/database-sharding-a-system-design-concept/",
        "https://www.geeksforgeeks.org/system-design/block-object-and-file-storage-in-cloud-with-difference/",
        "https://www.geeksforgeeks.org/dbms/introduction-of-database-normalization/",
        "https://www.geeksforgeeks.org/sql/best-practices-for-sql-query-optimizations/",
        "https://www.geeksforgeeks.org/dbms/denormalization-in-databases/",
        "https://www.geeksforgeeks.org/system-design/introduction-to-redis-server/",
        "https://www.geeksforgeeks.org/system-design/availability-in-system-design/",
        "https://www.geeksforgeeks.org/system-design/what-is-high-availability-in-system-design/",
        "https://www.geeksforgeeks.org/system-design/consistency-in-system-design/",
        "https://www.geeksforgeeks.org/system-design/consistency-patterns/",
        "https://www.geeksforgeeks.org/system-design/cap-theorem-in-system-design/",
        "https://www.geeksforgeeks.org/system-design/reliability-in-system-design/",
        "https://www.geeksforgeeks.org/system-design/fault-tolerance-in-system-design/",
        "https://www.geeksforgeeks.org/system-design/maintainability-in-system-design/",
        "https://www.geeksforgeeks.org/system-design/what-is-load-balancer-system-design/",
        "https://www.geeksforgeeks.org/system-design/load-balancing-algorithms/",
        "https://www.geeksforgeeks.org/operating-systems/difference-between-concurrency-and-parallelism/",
        "https://www.geeksforgeeks.org/system-design/stateless-vs-stateful-load-balancing/",
        "https://www.geeksforgeeks.org/system-design/load-balancing-vs-failover/",
        "https://www.geeksforgeeks.org/system-design/consistent-hashing/",
        "https://www.geeksforgeeks.org/system-design/latency-in-system-design/",
        "https://www.geeksforgeeks.org/system-design/caching-system-design-concept-for-beginners/",
        "https://www.geeksforgeeks.org/system-design/design-distributed-cache-system-design/",
        "https://www.geeksforgeeks.org/system-design/edge-caching-system-design/",
        "https://www.geeksforgeeks.org/system-design/cache-eviction-policies-system-design/",
        "https://www.geeksforgeeks.org/system-design/cold-and-warm-cache-in-system-design/",
        "https://www.geeksforgeeks.org/system-design/what-is-api-gateway-system-design/",
        "https://www.geeksforgeeks.org/system-design/message-queues-system-design/",
        "https://www.geeksforgeeks.org/system-design/rate-limiting-in-system-design/",
        "https://www.geeksforgeeks.org/system-design/rate-limiting-algorithms-system-design/",
        "https://www.geeksforgeeks.org/system-design/communication-protocols-in-system-design/",
        "https://www.geeksforgeeks.org/computer-networks/domain-name-system-dns-in-application-layer/",
        "https://www.geeksforgeeks.org/computer-networks/what-is-dns-caching/",
        "https://www.geeksforgeeks.org/computer-networks/what-is-time-to-live-ttl/",
        "https://www.geeksforgeeks.org/system-design/what-is-content-delivery-networkcdn-in-system-design/",
        "https://www.geeksforgeeks.org/system-design/network-protocols-and-proxies-in-system-design/",
        "https://www.geeksforgeeks.org/system-design/difference-between-forward-proxy-and-reverse-proxy/",
        "https://www.geeksforgeeks.org/javascript/what-is-long-polling-and-short-polling/",
        "https://www.geeksforgeeks.org/web-tech/what-is-web-socket-and-how-it-is-different-from-the-http/",
        "https://www.geeksforgeeks.org/system-design/event-sourcing-pattern/",
        "https://www.geeksforgeeks.org/system-design/event-sourcing-vs-event-streaming-in-system-design/",
        "https://www.geeksforgeeks.org/system-design/event-driven-apis-in-microservice-architectures/",
        "https://www.geeksforgeeks.org/system-design/error-handling-in-event-driven-architecture/",
        "https://www.geeksforgeeks.org/system-design/how-to-restore-state-in-an-event-based-message-driven-microservice-architecture-on-failure-scenario/",
        "https://www.geeksforgeeks.org/system-design/event-driven-architecture-patterns-in-cloud-native-applications/",
        "https://www.geeksforgeeks.org/system-design/request-driven-vs-event-driven-microservices/",
        "https://www.geeksforgeeks.org/system-design/event-driven-architecture-vs-microservices-architecture/",
        "https://www.geeksforgeeks.org/system-design/message-driven-architecture-vs-event-driven-architecture/",
        "https://www.geeksforgeeks.org/software-testing/unit-testing-software-testing/",
        "https://www.geeksforgeeks.org/software-testing/software-engineering-integration-testing/",
        "https://www.geeksforgeeks.org/system-design/cicd-pipeline-system-design/",
        "https://www.geeksforgeeks.org/system-design/essential-security-measures-in-system-design/",
        "https://www.geeksforgeeks.org/computer-networks/difference-between-authentication-and-authorization/",
        "https://www.geeksforgeeks.org/computer-networks/difference-between-secure-socket-layer-ssl-and-transport-layer-security-tls/",
        "https://www.geeksforgeeks.org/ethical-hacking/what-is-secure-software-development-life-cycle-ssdlc/",
        "https://www.geeksforgeeks.org/cloud-computing/what-is-data-backup-and-disaster-recovery/",
        "https://www.geeksforgeeks.org/computer-networks/what-is-a-distributed-system/",
        "https://www.geeksforgeeks.org/operating-systems/consensus-algorithms-in-distributed-system/",
        "https://www.geeksforgeeks.org/system-design/distributed-tracing-system-design/",
        "https://www.geeksforgeeks.org/operating-systems/secure-communication-in-distributed-system/",
        "https://www.geeksforgeeks.org/system-design/design-issues-of-distributed-system/",
        "https://www.geeksforgeeks.org/system-design/object-oriented-programingoop-concepts-for-designing-sytems/",
        "https://www.geeksforgeeks.org/system-design/inroduction-to-modularity-and-interfaces-in-system-design/",
        "https://www.geeksforgeeks.org/system-design/what-is-low-level-design-or-lld-learn-system-design/",
        "https://www.geeksforgeeks.org/system-design/solid-principle-in-programming-understand-with-real-life-examples/",
        "https://www.geeksforgeeks.org/software-engineering/dont-repeat-yourselfdry-in-software-development/",
        "https://www.geeksforgeeks.org/software-engineering/kiss-principle-in-software-development/",
        "https://www.geeksforgeeks.org/software-engineering/what-is-yagni-principle-you-arent-gonna-need-it/",
        "https://www.geeksforgeeks.org/system-design/unified-modeling-language-uml-introduction/",
        "https://www.geeksforgeeks.org/system-design/software-design-patterns/",
        "https://www.geeksforgeeks.org/system-design/system-design-url-shortening-service/",
        "https://www.geeksforgeeks.org/system-design/design-dropbox-a-system-design-interview-question/",
        "https://www.geeksforgeeks.org/interview-experiences/design-twitter-a-system-design-interview-question/",
        "https://www.geeksforgeeks.org/system-design/system-design-netflix-a-complete-architecture/",
        "https://www.geeksforgeeks.org/system-design/system-design-of-uber-app-uber-system-architecture/",
        "https://www.geeksforgeeks.org/system-design/design-bookmyshow-a-system-design-interview-question/",
        "https://www.geeksforgeeks.org/system-design/desiging-facebook-messenger-system-design-interview/",
        "https://www.geeksforgeeks.org/system-design/designing-whatsapp-messenger-system-design/",
        "https://www.geeksforgeeks.org/system-design/design-instagram-a-system-design-interview-question/",
        "https://www.geeksforgeeks.org/system-design/system-design-of-airline-management-system/",
        "https://www.geeksforgeeks.org/system-design/how-to-crack-system-design-round-in-interviews/",
        "https://www.geeksforgeeks.org/system-design/5-tips-to-crack-low-level-system-design-interviews/",
        "https://www.geeksforgeeks.org/system-design/5-common-system-design-concepts-for-interview-preparation/",
        "https://www.geeksforgeeks.org/interview-experiences/steps-to-approach-object-oriented-design-questions-in-interview/",
        "https://github.com/Jeevan-kumar-Raj/Grokking-System-Design",
        "https://www.geeksforgeeks.org/software-engineering/software-cost-estimation/",
        "https://www.geeksforgeeks.org/system-design/optimization-techniques-for-system-design/",
        "https://www.geeksforgeeks.org/system-design/cost-vs-performance/",
        "https://www.tryexponent.com/blog/system-design-interview-guide",
        "https://interviewing.io/guides/system-design-interview",
        "https://newsletter.systemdesign.one/p/how-to-prepare-for-system-design-interview",
        "https://roadmap.sh/questions/system-design",
        "https://medium.com/javarevisited/system-design-cheatsheet-4607e716db5a",
        "https://www.naukri.com/code360/library/system-design-interview-questions",
        "https://bytebytego.com/courses/system-design-interview/a-framework-for-system-design-interviews",
        "https://www.systemdesignhandbook.com/guides/system-design-interview-questions/",
    ]



    

    ingest_web(urls)