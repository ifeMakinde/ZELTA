import PageHeader from "@/components/PageHeader";

function Page() {
  return (
    <section className="space-y-6">
      <PageHeader
        title="Good morning"
        description="Here's your financial intelligence for today"
      />
      {/* Add dashboard widgets and cards here. The dashboard layout splits sidebar 30% / content 70%. */}
    </section>
  );
}

export default Page;
