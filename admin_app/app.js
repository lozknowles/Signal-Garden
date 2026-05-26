const { createElement: h, useEffect, useMemo, useState } = React;

const SOURCE_TYPES = [
  ["rss", "RSS / Atom feed"],
  ["url", "Blog or article URL"],
  ["x", "X feed bridge"],
  ["tweet", "Direct tweet URL"],
];

function extractUrls(text) {
  return [...(text || "").matchAll(/https?:\/\/[^\s<>"']+/g)].map((match) =>
    match[0].replace(/[.,);]+$/, "")
  );
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.error || "Request failed");
  return payload;
}

function useAdminState() {
  const [state, setState] = useState(null);
  const [status, setStatus] = useState(null);

  const reload = async () => {
    const payload = await api("/api/state");
    setState(payload);
  };

  useEffect(() => {
    reload().catch((error) =>
      setStatus({ type: "error", message: error.message })
    );
  }, []);

  return { state, setState, status, setStatus, reload };
}

function DropZone({ className, title, hint, onDropText }) {
  const [active, setActive] = useState(false);

  const handleDrop = async (event) => {
    event.preventDefault();
    setActive(false);
    const text =
      event.dataTransfer.getData("text/uri-list") ||
      event.dataTransfer.getData("text/plain");
    await onDropText(text);
  };

  return h(
    "div",
    {
      className: `dropzone ${className || ""} ${active ? "active" : ""}`,
      onDragEnter: (event) => {
        event.preventDefault();
        setActive(true);
      },
      onDragOver: (event) => event.preventDefault(),
      onDragLeave: () => setActive(false),
      onDrop: handleDrop,
    },
    h("div", null, h("div", { className: "drop-title" }, title), h("p", { className: "drop-hint" }, hint)),
    h("span", { className: "pill" }, "Drop URLs, selected text, or snippets")
  );
}

function Status({ status }) {
  if (!status) return null;
  return h("div", { className: `status ${status.type}` }, status.message);
}

function ListEditor({ title, values, onChange }) {
  const [draft, setDraft] = useState("");

  const add = () => {
    const value = draft.trim();
    if (!value || values.includes(value)) return;
    onChange([...values, value]);
    setDraft("");
  };

  return h(
    "section",
    { className: "panel" },
    h("h2", null, title),
    h(
      "div",
      { className: "list" },
      values.map((value, index) =>
        h(
          "div",
          { className: "row", key: `${value}-${index}` },
          h("div", { className: "row-title" }, value),
          h(
            "button",
            {
              className: "button",
              onClick: () => onChange(values.filter((_, i) => i !== index)),
            },
            "Remove"
          )
        )
      )
    ),
    h(
      "div",
      { className: "grid", style: { marginTop: 12 } },
      h("input", {
        className: "input",
        value: draft,
        onChange: (event) => setDraft(event.target.value),
        onKeyDown: (event) => {
          if (event.key === "Enter") add();
        },
      }),
      h("button", { className: "button primary", onClick: add }, "Add")
    )
  );
}

function Overview({ state }) {
  const config = state.config || {};
  return h(
    "section",
    { className: "panel" },
    h("h2", null, "Overview"),
    h(
      "div",
      { className: "grid" },
      h("div", null, h("h3", null, "Topics"), h("p", null, config.research_topics?.length || 0)),
      h("div", null, h("h3", null, "Preferred Sources"), h("p", null, config.preferred_sources?.length || 0)),
      h("div", null, h("h3", null, "Manual Clips"), h("p", null, Array.isArray(state.manual_clips) ? state.manual_clips.length : 0)),
      h("div", null, h("h3", null, "Personal Sources"), h("p", null, state.personal_sources?.sources?.length || 0))
    )
  );
}

function Inbox({ state, setState, setStatus }) {
  const [topic, setTopic] = useState("");
  const [sourceType, setSourceType] = useState("rss");

  const addManualClips = async (text) => {
    const urls = extractUrls(text);
    if (!urls.length) {
      setStatus({ type: "error", message: "No URL found in dropped text." });
      return;
    }

    const payload = await api("/api/manual-clips", {
      method: "POST",
      body: JSON.stringify({
        items: urls.map((url) => ({ url, topic, reason: text.trim() })),
      }),
    });
    setState({ ...state, manual_clips: payload.manual_clips });
    setStatus({ type: "ok", message: `Saved ${urls.length} manual clip(s).` });
  };

  const addPersonalSources = async (text) => {
    const urls = extractUrls(text);
    if (!urls.length) {
      setStatus({ type: "error", message: "No URL found in dropped text." });
      return;
    }

    const payload = await api("/api/personal-sources", {
      method: "POST",
      body: JSON.stringify({
        items: urls.map((url) => ({
          type: sourceType,
          url,
          feed_url: url,
          topic,
          reason: text.trim(),
        })),
      }),
    });
    setState({ ...state, personal_sources: payload.personal_sources });
    setStatus({ type: "ok", message: `Saved ${urls.length} personal source(s).` });
  };

  return h(
    React.Fragment,
    null,
    h(
      "section",
      { className: "panel" },
      h("h2", null, "Drop Settings"),
      h(
        "div",
        { className: "grid" },
        h(
          "label",
          { className: "field" },
          h("span", null, "Topic"),
          h("input", {
            className: "input",
            value: topic,
            onChange: (event) => setTopic(event.target.value),
            placeholder: "Optional topic override",
          })
        ),
        h(
          "label",
          { className: "field" },
          h("span", null, "Personal source type"),
          h(
            "select",
            {
              className: "select",
              value: sourceType,
              onChange: (event) => setSourceType(event.target.value),
            },
            SOURCE_TYPES.map(([value, label]) =>
              h("option", { key: value, value }, label)
            )
          )
        )
      )
    ),
    h(
      "div",
      { className: "grid" },
      h(DropZone, {
        className: "manual",
        title: "Manual Clips",
        hint: "Drop one-off read-later links, article snippets, or selected text. These are saved to Inbox/manual_clips.json.",
        onDropText: addManualClips,
      }),
      h(DropZone, {
        className: "personal",
        title: "Personal Sources",
        hint: "Drop RSS/Atom feeds, blog URLs, direct tweet URLs, or X feed bridge URLs. These are saved to Inbox/personal_sources.json.",
        onDropText: addPersonalSources,
      })
    ),
    h(
      "section",
      { className: "panel" },
      h("h2", null, "Saved Inbox Items"),
      h("h3", null, "Manual Clips"),
      h(
        "div",
        { className: "list" },
        (state.manual_clips || []).slice(-8).map((clip, index) =>
          h("div", { className: "row", key: `${clip.url}-${index}` }, h("div", null, h("div", { className: "row-title" }, clip.url), h("div", { className: "small" }, clip.topic || "No topic")))
        )
      ),
      h("h3", { style: { marginTop: 18 } }, "Personal Sources"),
      h(
        "div",
        { className: "list" },
        (state.personal_sources?.sources || []).slice(-8).map((source, index) =>
          h("div", { className: "row", key: `${source.url || source.feed_url}-${index}` }, h("div", null, h("div", { className: "row-title" }, source.url || source.feed_url), h("div", { className: "small" }, `${source.type || "url"} · ${source.topic || "No topic"}`)))
        )
      )
    )
  );
}

function Config({ state, setState, setStatus }) {
  const [config, setConfig] = useState(state.config || {});
  const [raw, setRaw] = useState(JSON.stringify(state.config || {}, null, 2));

  const updateList = (key, values) => {
    const next = { ...config, [key]: values };
    setConfig(next);
    setRaw(JSON.stringify(next, null, 2));
  };

  const save = async () => {
    let parsed;
    try {
      parsed = JSON.parse(raw);
    } catch (error) {
      setStatus({ type: "error", message: error.message });
      return;
    }

    const payload = await api("/api/config", {
      method: "POST",
      body: JSON.stringify({ config: parsed }),
    });
    setConfig(payload.config);
    setRaw(JSON.stringify(payload.config, null, 2));
    setState({ ...state, config: payload.config });
    setStatus({ type: "ok", message: "Saved areas.json." });
  };

  return h(
    React.Fragment,
    null,
    h(
      "div",
      { className: "grid" },
      h(ListEditor, {
        title: "Research Topics",
        values: config.research_topics || [],
        onChange: (values) => updateList("research_topics", values),
      }),
      h(ListEditor, {
        title: "Preferred Sources",
        values: config.preferred_sources || [],
        onChange: (values) => updateList("preferred_sources", values),
      })
    ),
    h(
      "section",
      { className: "panel" },
      h("h2", null, "Raw areas.json"),
      h("textarea", {
        className: "textarea",
        style: { minHeight: 420, fontFamily: "Consolas, monospace" },
        value: raw,
        onChange: (event) => setRaw(event.target.value),
      }),
      h("div", { style: { marginTop: 12 } }, h("button", { className: "button primary", onClick: save }, "Save Config"))
    )
  );
}

function App() {
  const { state, setState, status, setStatus, reload } = useAdminState();
  const [tab, setTab] = useState("overview");

  const tabs = useMemo(
    () => [
      ["overview", "Overview"],
      ["inbox", "Clips & Sources"],
      ["config", "Config"],
    ],
    []
  );

  if (!state) {
    return h("div", { className: "shell" }, h("div", { className: "topbar" }, h("div", { className: "title" }, "Signal Garden Admin")), h("main", { className: "layout" }, h("section", { className: "panel" }, "Loading...")));
  }

  return h(
    "div",
    { className: "shell" },
    h(
      "header",
      { className: "topbar" },
      h("div", null, h("div", { className: "title" }, "Signal Garden Admin"), h("div", { className: "subtitle" }, "React control surface for research topics, personal sources, and inbox clips")),
      h("div", { className: "actions" }, h("button", { className: "button ghost", onClick: reload }, "Reload"))
    ),
    h(
      "main",
      { className: "layout" },
      h(
        "aside",
        { className: "sidebar" },
        h(
          "nav",
          { className: "nav" },
          tabs.map(([key, label]) =>
            h("button", { key, className: tab === key ? "active" : "", onClick: () => setTab(key) }, label)
          )
        ),
        h("div", { className: "pathbox" }, h("strong", null, "Vault"), h("div", null, state.paths?.vault), h("strong", null, "Config"), h("div", null, state.paths?.config))
      ),
      h(
        "section",
        { className: "content" },
        h(Status, { status }),
        tab === "overview" && h(Overview, { state }),
        tab === "inbox" && h(Inbox, { state, setState, setStatus }),
        tab === "config" && h(Config, { state, setState, setStatus })
      )
    )
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(h(App));
