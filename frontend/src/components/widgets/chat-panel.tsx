import { useEffect, useState } from "react";import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { sendToAI } from "@/components/api/ai";

type Message = {
  role: "user" | "assistant";
  text: string;
};


const STORAGE_KEY = "chat-messages";

export const buildAIContext = (tasks: any[] = [], selectedTask?: any) => {
	
  const ganttTasks = tasks.map((t) => ({
  id: String(t.id),
  text: t.text,
  type: t.type,
  open: t.open ?? false,
  assignee: t.assignee ?? "",
  start: t.start ?? null,
  duration: t.duration ?? 0,
  progress: t.progress ?? 0,
  parent: t.parent ?? null,
}));

console.log("========== TASKS ==========");
console.log(ganttTasks);
console.table(ganttTasks);

console.log("AI TASKS CONTEXT:");
console.table(
  ganttTasks.map(t => ({
    id: t.id,
    text: t.text
  }))
);

  const context = {
    context_version: "1.0",

    project: {
      name: "Gantt AI Project",
    },

    tasks: ganttTasks,

    relationships: ganttTasks
      .filter((t) => t.parent)
      .map((t) => ({
        parent: t.parent,
        child: t.id,
      })),

    ui_state: {
      selected_task_id: selectedTask?.id ?? null,
    },
  };

  return context;
};

export default function ChatPanel({
  width,
  tasks,
  selectedTask,
}: {
  width: number;
  tasks: any[];
  selectedTask?: any;
}) {
  const API_URL = import.meta.env.VITE_API_URL;

  const [messages, setMessages] = useState<Message[]>(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });

  const [input, setInput] = useState("");
  const [uploadOpen, setUploadOpen] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
  }, [messages]);

	const sendMessage = async () => {
	  if (!input.trim()) return;

	  const userText = input;

	  const context = buildAIContext(
	    tasks,
	    selectedTask
	  );

	  console.log("📤 SEND TO AI:", {
	    message: userText,
	    context,
	  });


  setMessages((prev) => [
    ...prev,
    {
      role: "user",
      text: userText,
    },
  ]);


  setInput("");


  try {

    const data = await sendToAI(
      userText,
      context
    );


    console.log(
      "🤖 AI RESPONSE:",
      data
    );


    if (
      data.action === "create_task" ||
      data.action === "update_task" ||
      data.action === "delete_task"
    ) {

      console.log(
        "🚀 SEND COMMAND TO GANTT:",
        data
      );


      window.dispatchEvent(
        new CustomEvent(
          "gantt-command",
          {
            detail: data,
          }
        )
      );


      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: "Готово",
        },
      ]);


      return;
    }


    const answer =
      data?.message ??
      "AI не вернул ответ.";


    setMessages((prev) => [
      ...prev,
      {
        role: "assistant",
        text: answer,
      },
    ]);


  } catch (error: any) {

    console.error(
      "AI ERROR:",
      error
    );


    setMessages((prev) => [
      ...prev,
      {
        role: "assistant",
        text: `Ошибка AI: ${error.message}`,
      },
    ]);

  }
};

  const handleUpload = () => {
  if (!file) return;


  console.log("UPLOAD CLICK:", file);


  const isExcel =
    file.name.toLowerCase().endsWith(".xlsx") ||
    file.name.toLowerCase().endsWith(".xls");


  if (!isExcel) {
    setError("Можно загружать только Excel (.xls, .xlsx)");
    return;
  }


  const event = new CustomEvent(
    "excel-upload",
    {
      detail: file,
    }
  );


  console.log(
    "DISPATCH EXCEL EVENT:",
    event
  );


  window.dispatchEvent(event);


  setFile(null);
  setUploadOpen(false);
};

  const handleExport = async () => {
    const res = await fetch(`${API_URL}/export-excel`);
    const blob = await res.blob();

    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "gantt.xlsx";
    a.click();

    window.URL.revokeObjectURL(url);
  };

  return (
    <div style={{ width }} className="border-l bg-white flex flex-col h-full">
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.map((m, i) => (
          <div
            key={i}
            className={`text-sm px-3 py-2 rounded-2xl max-w-[85%] ${
              m.role === "user"
                ? "bg-blue-500 text-white ml-auto"
                : "bg-gray-100 text-gray-900"
            }`}
          >
            {m.text}
          </div>
        ))}
      </div>

      <div className="p-3 border-t bg-white">
        <div className="flex flex-col gap-2">
          <Textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Напишите сообщение..."
            className="min-h-30 resize-none bg-gray-100 text-sm border border-gray-200 rounded-xl focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-0 focus-visible:outline-none"
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
              }
            }}
          />

          <Button
            onClick={sendMessage}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white cursor-pointer"
          >
            Отправить →
          </Button>

          <div className="flex gap-2">
            <Button
              variant="outline"
              className="w-1/2 text-xs cursor-pointer bg-gray-200 hover:bg-gray-300 transition"
              onClick={() => setUploadOpen(true)}
            >
              📥 Импорт
            </Button>

            <Button
              variant="outline"
              className="w-1/2 text-xs cursor-pointer bg-gray-200 hover:bg-gray-300 transition"
              onClick={handleExport}
            >
              📤 Экспорт
            </Button>
          </div>
        </div>
      </div>

      <Dialog open={uploadOpen} onOpenChange={setUploadOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Загрузка Excel</DialogTitle>
          </DialogHeader>

          <input
            type="file"
            onChange={(e) => {
              setFile(e.target.files?.[0] || null);
              setError("");
            }}
          />

          {error && <div className="text-red-500 text-sm">{error}</div>}

          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setUploadOpen(false)}>
              Отмена
            </Button>
            <Button disabled={!file} onClick={handleUpload}>
              Загрузить
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}