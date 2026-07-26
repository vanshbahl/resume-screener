export function Footer() {
  return (
    <footer className="py-12 bg-white border-t border-slate-100">
      <div className="max-w-6xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-6">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 bg-indigo-600 rounded-md" />
          <span className="font-semibold text-slate-900">Resume Intelligence</span>
        </div>
        
        <div className="flex gap-8 text-sm font-medium text-slate-500">
          <a href="#" className="hover:text-slate-900 transition-colors">Privacy Policy</a>
          <a href="#" className="hover:text-slate-900 transition-colors">Terms of Service</a>
          <a href="#" className="hover:text-slate-900 transition-colors">Contact</a>
        </div>
        
        <div className="text-sm text-slate-400">
          © {new Date().getFullYear()} Resume Intelligence. All rights reserved.
        </div>
      </div>
    </footer>
  );
}
